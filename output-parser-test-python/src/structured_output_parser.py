"""
对应 output-parser-test/src/structured-output-parser.mjs

说明：LangChain Python 新版（langchain_core 1.x）已从
langchain_core.output_parsers 中移除 StructuredOutputParser。
与 JS 的 StructuredOutputParser.fromNamesAndDescriptions 最接近的写法是：
PydanticOutputParser + Pydantic 模型（字段名 + description）。
"""
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser

load_dotenv()


class EinsteinInfo(BaseModel):
  """与 JS 里 fromNamesAndDescriptions 的字段对应"""

  name: str = Field(description="姓名")
  birth_year: int = Field(description="出生年份")
  nationality: str = Field(description="国籍")
  major_achievements: str = Field(description="主要成就，用逗号分隔的字符串")
  famous_theory: str = Field(description="著名理论")


model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)

parser = PydanticOutputParser(pydantic_object=EinsteinInfo)

question = f"""请介绍一下爱因斯坦的信息。

{parser.get_format_instructions()}"""

if __name__ == "__main__":
  print("question:", question)
  try:
    print("🤔 正在调用大模型（使用 PydanticOutputParser）...\n")

    response = model.invoke(question)

    print("📤 模型原始响应:\n")
    print(response.content)

    result = parser.parse(response.content)

    print("\n✅ 解析结果:\n")
    print(result)
    print(f"姓名: {result.name}")
    print(f"出生年份: {result.birth_year}")
    print(f"国籍: {result.nationality}")
    print(f"著名理论: {result.famous_theory}")
    print(f"主要成就: {result.major_achievements}")

  except Exception as e:
    print(f"❌ 错误: {e}")
