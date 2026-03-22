"""
对应 output-parser-test/src/stream-tool-calls-parser.mjs

增量打印说明：json.dumps 在字段变化时，新串不一定是旧串的「后缀延长」
（键序、缩进、整段重排都会导致失败）。因此仅当 current 以 last 为前缀时才 slice；
否则整段重打并换行分隔。
"""
import json
import os
import sys
from typing import Any, Optional

from dotenv import load_dotenv
from langchain_core.output_parsers.openai_tools import JsonOutputToolsParser
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


class Scientist(BaseModel):
  name: str = Field(description="科学家的全名")
  birth_year: int = Field(description="出生年份")
  death_year: Optional[int] = Field(
      default=None, description="去世年份，如果还在世则不填"
  )
  nationality: str = Field(description="国籍")
  fields: list[str] = Field(description="研究领域列表")
  achievements: list[str] = Field(description="主要成就")
  biography: str = Field(description="简短传记")


@tool(args_schema=Scientist)
def extract_scientist_info(**kwargs: object) -> str:
  """提取和结构化科学家的详细信息。"""
  return ""


model_with_tool = model.bind_tools([extract_scientist_info])
parser = JsonOutputToolsParser()
chain = model_with_tool | parser


def _dumps_args(args: Any) -> str:
  return json.dumps(
      args or {},
      ensure_ascii=False,
      indent=2,
      sort_keys=True,
  )


def main() -> None:
  try:
    stream = chain.stream("详细介绍牛顿的生平和成就")

    last_content = ""
    final_result: Any = None

    print("📡 实时输出流式内容（增量；非单调时自动整段重印）:\n")

    for chunk in stream:
      if not chunk:
        continue

      tool_call = chunk[0]
      args = (
          tool_call.get("args", {})
          if isinstance(tool_call, dict)
          else {}
      )

      current_content = _dumps_args(args)

      if last_content and current_content.startswith(last_content):
        new_text = current_content[len(last_content):]
        if new_text:
          print(new_text, end="", flush=True)
      else:
        # 新串不是旧串前缀：不能 slice，否则乱码
        if last_content:
          print(
              "\n\n# （JSON 序列化与前一轮不兼容前缀，以下为当前全文）\n",
              end="",
              flush=True,
          )
        print(current_content, end="", flush=True)

      last_content = current_content
      final_result = args

    print("\n\n✅ 流式输出完成")

    if final_result is not None:
      print("\n🎯 最终结构化结果:")
      print(json.dumps(final_result, ensure_ascii=False, indent=2))

  except Exception as e:
    print(f"\n❌ 错误: {e}", file=sys.stderr)
    raise


if __name__ == "__main__":
  main()
