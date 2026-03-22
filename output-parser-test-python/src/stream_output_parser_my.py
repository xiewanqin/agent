"""
对应 output-parser-test/src/stream-structured-partial.mjs

流程：普通 model.stream → 拼接字符串 → 流结束后 PydanticOutputParser.parse 一次
（不是 with_structured_output 那种「每块已是对象」的流）
"""
import json
import os
import sys

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

load_dotenv()

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
    timeout=float(os.getenv("STREAM_REQUEST_TIMEOUT", "120")),
)


class Scientist(BaseModel):
  name: str = Field(description="姓名")
  birth_year: int = Field(description="出生年份")
  death_year: int = Field(description="去世年份")
  nationality: str = Field(description="国籍")
  occupation: str = Field(description="职业")
  famous_works: list[str] = Field(description="著名作品列表")
  biography: str = Field(description="简短传记")


parser = PydanticOutputParser(pydantic_object=Scientist)

# 与 mjs 一致：莫扎特 + format instructions
prompt = f"详细介绍莫扎特的信息。\n\n{parser.get_format_instructions()}"


def _chunk_text(chunk) -> str:
  c = getattr(chunk, "content", None)
  if c is None:
    return ""
  if isinstance(c, str):
    return c
  if isinstance(c, list):
    parts: list[str] = []
    for block in c:
      if isinstance(block, str):
        parts.append(block)
      elif isinstance(block, dict) and block.get("type") == "text":
        parts.append(str(block.get("text", "")))
    return "".join(parts)
  return str(c)


def main() -> None:
  print("🌊 流式结构化输出演示（先流式文本，再一次性 parse）\n")

  try:
    stream = model.stream(prompt)  # stream 是迭代器
    full_content = ""
    chunk_count = 0

    print("📡 接收流式数据:\n")

    for chunk in stream:
      chunk_count += 1
      text = _chunk_text(chunk)
      full_content += text
      print(text, end="", flush=True)

    print(f"\n\n✅ 共接收 {chunk_count} 个数据块\n")

    result = parser.parse(full_content)

    print("📊 解析后的结构化结果:\n")
    print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))

    print("\n📝 格式化输出:")
    print(f"姓名: {result.name}")
    print(f"出生年份: {result.birth_year}")
    print(f"去世年份: {result.death_year}")
    print(f"国籍: {result.nationality}")
    print(f"职业: {result.occupation}")
    print(f"著名作品: {', '.join(result.famous_works)}")
    print(f"传记: {result.biography}")

  except Exception as e:
    print(f"\n❌ 错误: {e}", file=sys.stderr)
    raise


if __name__ == "__main__":
  main()
