"""
对比 smart_import.py：
- smart_import：with_structured_output → 直接拿到 Pydantic → 自己 executemany
- 本文件：Agent + @tool(insert_friends)，模型通过 tool_calls 把结构化数据交给工具写库

下面 main() 里的打印格式刻意与 smart_import 对齐，便于对照两种写法。
"""
import json
import os
from typing import List, Optional

import pymysql
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from pydantic import BaseModel, Field

load_dotenv()

# ---------------------------
# 1️⃣ 模型
# ---------------------------
model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)

# ---------------------------
# 2️⃣ Schema（结构化输入给工具）
# ---------------------------


class Friend(BaseModel):
  name: str = Field(description="姓名")
  gender: str = Field(description="性别（男/女）")
  birth_date: str = Field(description="出生日期 YYYY-MM-DD")
  company: Optional[str] = Field(default=None)
  title: Optional[str] = Field(default=None)
  phone: Optional[str] = Field(default=None)
  wechat: Optional[str] = Field(default=None)


class FriendsInput(BaseModel):
  friends: List[Friend] = Field(description="好友列表，多人时必须一次性传入")


# ---------------------------
# 3️⃣ MySQL Tool
# ---------------------------
CONNECTION_KW = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "admin",
    "database": "hello",
    "charset": "utf8mb4",
}


@tool
def insert_friends(data: FriendsInput) -> str:
  """将好友信息写入 MySQL 数据库"""

  connection = pymysql.connect(**CONNECTION_KW, cursorclass=pymysql.cursors.DictCursor)

  try:
    with connection.cursor() as cursor:
      insert_sql = """
                INSERT INTO friends (
                    name, gender, birth_date, company, title, phone, wechat
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

      values = [
          (
              f.name,
              f.gender,
              f.birth_date,
              f.company,
              f.title,
              f.phone,
              f.wechat,
          )
          for f in data.friends
      ]

      cursor.executemany(insert_sql, values)
      connection.commit()

      n = len(values)
      first_id = cursor.lastrowid
      ids_hint = (
          f"，推测自增 ID 区间 [{first_id} .. {first_id + n - 1}]"
          if first_id and n
          else ""
      )
      return f"成功插入 {n} 条数据{ids_hint}"

  except Exception as e:
    connection.rollback()
    return f"插入失败: {str(e)}"

  finally:
    connection.close()


# ---------------------------
# 4️⃣ Agent
# ---------------------------
agent = create_agent(
    model=model,
    tools=[insert_friends],
    system_prompt="""
你是一个信息提取助手。

你的任务：
1. 从用户输入文本中提取所有“好友信息”
2. 转换成结构化数据
3. 调用 insert_friends 工具写入数据库

字段要求：
- name: 姓名
- gender: 男/女
- birth_date: YYYY-MM-DD（可以估算）
- company: 可为空
- title: 可为空
- phone: 可为空
- wechat: 可为空

重要规则：
- 如果有多个人，必须一次性调用工具（传入数组）
- 不要返回文本，直接调用工具
""",
)


def _tool_call_name_args(tc) -> tuple[str, dict]:
  """兼容 dict / LangChain ToolCall 对象。"""
  if isinstance(tc, dict):
    return tc.get("name") or "?", tc.get("args") or {}
  name = getattr(tc, "name", None) or "?"
  args = getattr(tc, "args", None)
  if args is None and hasattr(tc, "get"):
    args = tc.get("args", {})
  return name, args if isinstance(args, dict) else {}


def print_agent_result_vs_smart_import(result: dict) -> None:
  """
  与 smart_import.py 对齐的观感：
  - 「提取」对应：模型发出的 insert_friends 的 args（即结构化好友列表）
  - 「插入结果」对应：ToolMessage 里工具的返回字符串
  """
  messages = result.get("messages") or []
  print("\n" + "=" * 60)
  print("📌 本脚本：Agent + insert_friends 工具（对照 smart_import 的打印节奏）")
  print("=" * 60)

  print("\n🤔 正在从文本中提取信息（由模型通过工具调用完成）…\n")

  insert_args_printed = False
  insert_tool_reply: Optional[str] = None

  for i, msg in enumerate(messages, 1):
    label = f"--- 步骤 {i}: {type(msg).__name__} ---"
    print(label)

    if isinstance(msg, HumanMessage):
      text = msg.content if isinstance(msg.content, str) else str(msg.content)
      preview = text if len(text) <= 400 else text[:400] + "\n…（已截断）"
      print("【用户输入】\n", preview, sep="")

    elif isinstance(msg, AIMessage):
      if msg.content:
        print("【模型文本】\n", msg.content, sep="")
      tcs = getattr(msg, "tool_calls", None) or []
      if tcs:
        for tc in tcs:
          name, args = _tool_call_name_args(tc)
          print(f"\n🔧 工具调用: {name}")
          print(json.dumps(args, ensure_ascii=False, indent=2))
          if name == "insert_friends" and not insert_args_printed:
            insert_args_printed = True
            friends = args.get("data", {}).get("friends", args.get("friends"))
            if friends is not None:
              n = len(friends) if isinstance(friends, list) else 0
              print(f"\n✅ （等价于 smart_import）提取到 {n} 条结构化信息（见上方 JSON 的 friends）")
            else:
              print("\n✅ 模型已发起 insert_friends（参数结构见上方 JSON）")

    elif isinstance(msg, ToolMessage):
      print(f"【工具 {msg.name} 返回】\n{msg.content}")
      if msg.name == "insert_friends":
        insert_tool_reply = str(msg.content)

    print()

  print("=" * 60)
  print("🎉 处理完成（Agent 路径）")
  print("=" * 60)
  if insert_tool_reply:
    print("   写入结果：", insert_tool_reply)
  last = messages[-1] if messages else None
  if isinstance(last, AIMessage) and last.content:
    print("\n【模型最终回复】\n", last.content, sep="")


def main() -> None:
  sample_text = """我最近认识了几个新朋友。第一个是张总1，女的，看起来32出头，在腾讯做总监，手机13200138000，微信是zhangzong20242。
第二个是李工1，男，大概29岁，在阿里云做架构师1，电话15902159000，微信号lee_arch1。
还有一个是陈经理1，女，32岁左右，在美团做产品，手机号是18800488000，微信chenpm20224。"""

  result = agent.invoke({"messages": [{"role": "user", "content": sample_text}]})

  print_agent_result_vs_smart_import(result)


if __name__ == "__main__":
  main()
