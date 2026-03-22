"""
用了 withStructuredOutput 之后，它会在 json 生成完通过校验后再返回（底层是 tool calls）。所以只有一个 chunk 包含完整 json这样明显不是真的流式。
"""
import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# 加载环境变量
load_dotenv()

# 初始化模型
model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)

# 定义结构化输出模型


class Scientist(BaseModel):
  name: str = Field(description="姓名")
  birth_year: int = Field(description="出生年份")
  death_year: int = Field(description="去世年份")
  nationality: str = Field(description="国籍")
  occupation: str = Field(description="职业")
  famous_works: list[str] = Field(description="著名作品列表")
  biography: str = Field(description="简短传记")


# 创建结构化模型
structured_model = model.with_structured_output(Scientist)

# 提示词
prompt = "详细介绍莫扎特的信息。json 格式输出"

print("🌊 流式结构化输出演示（withStructuredOutput）")

try:
  # 流式调用
  stream = structured_model.stream(prompt)
  chunk_count = 0
  result = None

  for chunk in stream:
    chunk_count += 1
    result = chunk
    print(f"[Chunk {chunk_count}] 收到数据块")

    # 方法1：使用 model_dump() 转换为字典（推荐）
    chunk_dict = chunk.model_dump()
    print(f"当前块内容: {json.dumps(chunk_dict, ensure_ascii=False, indent=2)}")

    # 方法2：如果需要更详细的调试信息
    # print(f"块类型: {type(chunk)}")
    # print(f"块内容: {chunk}")

  # 打印最终结果
  if result:
    print("\n📊 最终结构化结果:")
    # 使用 model_dump() 转换整个对象
    result_dict = result.model_dump()
    print(json.dumps(result_dict, ensure_ascii=False, indent=2))

    # 也可以直接访问属性
    print(f"\n📝 关键信息:")
    print(f"姓名: {result.name}")
    print(f"出生年份: {result.birth_year}")
    print(f"去世年份: {result.death_year}")
    print(f"国籍: {result.nationality}")
    print(f"职业: {result.occupation}")
    print(f"著名作品: {', '.join(result.famous_works)}")

except Exception as e:
  print(f"❌ 错误: {e}")
  import traceback
  traceback.print_exc()
finally:
  print(f"\n\n=== 统计信息 ===")
  print(f"共接收 {chunk_count} 个数据块")
  if result:
    print(f"最终结构化结果: {result.name} - {result.occupation}")
