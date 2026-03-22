"""
对应 output-parser-test/src/tool-calls-args.mjs

用 bind_tools + 工具 schema 让模型以 tool_calls 形式返回结构化参数，
只取 tool_calls[0].args，不执行后续 agent 循环。
"""
import json
import os

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)


class ScientistInfo(BaseModel):
  """与 zod scientistSchema 对应（工具参数 / 结构化抽取结果）"""

  name: str = Field(description="科学家的全名")
  birth_year: int = Field(description="出生年份")
  nationality: str = Field(description="国籍")
  fields: list[str] = Field(description="研究领域列表")


@tool(args_schema=ScientistInfo)
def extract_scientist_info(**kwargs: object) -> str:
  """提取和结构化科学家的详细信息"""
  return "ok"  # 占位实现：本示例只读 tool_calls 的 args，不会走到 agent 执行工具。


model_with_tools = model.bind_tools([extract_scientist_info])


def main() -> None:
  response = model_with_tools.invoke("介绍一下爱因斯坦")

  print("response.tool_calls:", response.tool_calls)

  if not response.tool_calls:
    print("模型未发起 tool_calls，原始内容:", response.content)
    return

  # LangChain 中 args 一般为 dict
  first = response.tool_calls[0]
  result = first.get("args") if isinstance(
      first, dict) else getattr(
      first, "args", first)

  # 这里用 json.dumps，是因为 result 一般是「工具参数字典」dict，你想在终端里看到 格式整齐、带缩进的 JSON 文本，而不是
  # Python 默认打印那种一行挤在一起的样子。
  print("结构化结果:", json.dumps(result, ensure_ascii=False, indent=2))
  print(f"\n姓名: {result['name']}")
  print(f"出生年份: {result['birth_year']}")
  print(f"国籍: {result['nationality']}")
  print(f"研究领域: {', '.join(result['fields'])}")


if __name__ == "__main__":
  main()
