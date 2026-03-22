"""
对应 output-parser-test/src/xml-output-parser.mjs

依赖：langchain 的 XMLOutputParser 需要单独安装 defusedxml（已写入 pyproject.toml）。
"""
import os
import json
import sys

from dotenv import load_dotenv
from langchain_core.output_parsers import XMLOutputParser
from langchain_openai import ChatOpenAI

load_dotenv()

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)

parser = XMLOutputParser()

question = f"""请提取以下文本中的人物信息：阿尔伯特·爱因斯坦出生于 1879 年，是一位伟大的物理学家。

{parser.get_format_instructions()}"""


def main() -> None:
  print("question:", question)

  try:
    print("🤔 正在调用大模型（使用 XMLOutputParser）...\n")

    response = model.invoke(question)

    print("📤 模型原始响应:\n")
    print(response.content)

    result = parser.parse(response.content)

    print("\n✅ XMLOutputParser 自动解析的结果:\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))

  except Exception as e:
    print(f"❌ 错误: {e}", file=sys.stderr)
    raise


if __name__ == "__main__":
  main()
