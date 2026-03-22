"""
对应 output-parser-test/src/test/smart-import.mjs

注意：Python 的 with_structured_output 需要 Pydantic BaseModel，
不能传 typing.List[Friend]，要用「根模型」包一层 list 字段。
"""
import json
import os
import sys

import pymysql
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)


class Friend(BaseModel):
    name: str = Field(description="姓名")
    gender: str = Field(description="性别（男/女）")
    birth_date: str = Field(
        description="出生日期，格式：YYYY-MM-DD，如果无法确定具体日期，根据年龄估算"
    )
    company: str | None = Field(default=None, description="公司名称，如果没有则返回 None")
    title: str | None = Field(default=None, description="职位/头衔，如果没有则返回 None")
    phone: str | None = Field(default=None, description="手机号，如果没有则返回 None")
    wechat: str | None = Field(default=None, description="微信号，如果没有则返回 None")


class FriendsBatch(BaseModel):
    """根模型：与 z.array(friendSchema) 对应，模型返回 { friends: [...] }"""

    friends: list[Friend] = Field(description="好友信息数组，即使只有一人也要放在列表里")


structured_model = model.with_structured_output(FriendsBatch)

CONNECTION_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "admin",
    "database": "hello",
    "charset": "utf8mb4",
    "autocommit": False,
}


def extract_and_insert(text: str) -> dict:
    connection = pymysql.connect(**CONNECTION_CONFIG)
    try:
        with connection.cursor() as cursor:
            cursor.execute("USE hello;")

            print("🤔 正在从文本中提取信息...\n")
            prompt = f"""请从以下文本中提取所有好友信息，文本中可能包含一个或多个人的信息。请将每个人的信息分别提取出来，返回一个数组。

{text}

要求：
1. 如果文本中包含多个人，请为每个人创建一个对象
2. 每个对象包含：姓名、性别、出生日期、公司、职位、手机号、微信号
3. 如果某个字段在文本中找不到，请返回 null
4. 即使只有一个人，也要放在 friends 数组里"""

            batch: FriendsBatch = structured_model.invoke(prompt)
            results = batch.friends

            print(f"✅ 提取到 {len(results)} 条结构化信息:")
            print(json.dumps(batch.model_dump(), ensure_ascii=False, indent=2))
            print()

            if len(results) == 0:
                print("⚠️  没有提取到任何信息")
                connection.commit()
                return {"count": 0, "insert_ids": []}

            insert_sql = """
            INSERT INTO friends (name, gender, birth_date, company, title, phone, wechat)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            # executemany 需要「元组列表」，顺序与 INSERT 列一致（不能传 dict 列表）
            rows = [
                (
                    f.name,
                    f.gender,
                    f.birth_date,
                    f.company,
                    f.title,
                    f.phone,
                    f.wechat,
                )
                for f in results
            ]
            cursor.executemany(insert_sql, rows)
            connection.commit()

            first_id = cursor.lastrowid
            n = len(rows)
            # 单次 INSERT 多行时，MySQL 自增 ID 通常连续；若不确定可只打印 first_id
            insert_ids = (
                list(range(first_id, first_id + n)) if first_id else []
            )

            print(f"✅ 成功插入 {n} 条记录")
            return {"count": n, "insert_ids": insert_ids}

    except Exception as e:
        print("❌ 执行出错：", e, file=sys.stderr)
        connection.rollback()
        return {"count": 0, "insert_ids": []}
    finally:
        connection.close()


def main() -> None:
    sample = """
  我最近认识了几个新朋友。第一个是张总，女的，看起来30出头，在腾讯做技术总监，手机13800138000，微信是zhangzong2024。第二个是李工，男，大概28岁，在阿里云做架构师，电话15900159000，微信号lee_arch。还有一个是陈经理，女，35岁左右，在美团做产品经理，手机号是18800188000，微信chenpm2024。
  """
    result = extract_and_insert(sample)
    print(f"🎉 处理完成！成功插入 {result['count']} 条记录")
    print(f"   插入的ID：{result['insert_ids']}")


if __name__ == "__main__":
    main()
