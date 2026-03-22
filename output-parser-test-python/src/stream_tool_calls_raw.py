"""
对照 output-parser-test/src/stream-tool-calls-raw.mjs

很多 OpenAI 兼容网关流式时 **没有** `tool_call_chunks`，只在
`additional_kwargs["tool_calls"][].function.arguments` 里增量给字符串，
只读 `tool_call_chunks[0]` 会一直空。

可选：`STREAM_FORCE_TOOL=1` → `tool_choice="required"`，减少模型只回正文、不调工具。
"""
import os
import sys

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()

_bind_kw: dict = {"parallel_tool_calls": False}
if os.getenv("STREAM_FORCE_TOOL", "").strip() in ("1", "true", "yes", "required"):
  _bind_kw["tool_choice"] = "required"

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)


class Scientist(BaseModel):
  name: str = Field(description="科学家的全名")
  birth_year: int = Field(description="出生年份")
  death_year: int | None = Field(
      default=None, description="去世年份，如果还在世则不填"
  )
  nationality: str = Field(description="国籍")
  fields: list[str] = Field(description="研究领域列表")
  achievements: list[str] = Field(description="主要成就")
  biography: str = Field(description="简短传记")


@tool(args_schema=Scientist)
def extract_scientist_info(**kwargs: object) -> str:
  """提取和结构化科学家的详细信息（本示例只看流式 args，可不实现逻辑）。"""
  return ""


model_with_tools = model.bind_tools([extract_scientist_info], **_bind_kw)


def main() -> None:
  print("🌊 流式 Tool Calls 演示 - 直接打印原始 tool_calls_chunk\n")

  try:
    stream = model_with_tools.stream("详细介绍牛顿的生平和成就")
    print("📡 实时输出流式 tool_calls_chunk:\n")

    args_parts = []  # 收集所有片段

    for chunk in stream:
      tcc = getattr(chunk, "tool_call_chunks", None) or []
      if tcc:
        first = tcc[0]
        frag = (
            first.get("args")
            if isinstance(first, dict)
            else (getattr(first, "args", None) or "")
        )
        if frag:
          args_parts.append(frag)
          print(frag, end="", flush=True)

    # 完整参数
    if args_parts:
      full_args = ''.join(args_parts)
      print(f"\n\n完整参数:\n{full_args}")

    print("\n✅ 流式输出完成")

  except Exception as e:
    print(f"\n❌ 错误: {e}", file=sys.stderr)
    raise


if __name__ == "__main__":
  main()
