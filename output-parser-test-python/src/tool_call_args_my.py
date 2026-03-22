"""
LangChain 1.x 结构化输出（对应 output-parser-test/src/tool-calls-args.mjs）

LC 1.2+ 中 ChatOpenAI.with_structured_output 默认 method=\"json_schema\"；
若自建 API 不支持 JSON Schema 响应格式，可改为 method=\"function_calling\"（走工具形态，更接近 JS bindTools）。
"""
import json
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()

# ========== 1. 初始化模型（LangChain 1.x + langchain-openai）==========
model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)

# ========== 2. 定义结构化 Schema（Pydantic，对应 zod scientistSchema）==========


class Scientist(BaseModel):
  name: str = Field(description="科学家的全名")
  birth_year: int = Field(description="出生年份")
  nationality: str = Field(description="国籍")
  fields: list[str] = Field(description="研究领域列表")


# ========== 3. 绑定结构化输出（LangChain 1.x 推荐）==========
# 默认 json_schema；兼容性问题见文件顶部说明
structured_model = model.with_structured_output(Scientist)

# 可选：与「仅 tool_calls 参数」更一致的绑定方式（不执行真实工具）
# structured_model = model.with_structured_output(
#     Scientist,
#     method="function_calling",
# )


def main() -> None:
  # ========== 4. 调用 ==========
  result: Scientist = structured_model.invoke("介绍一下爱因斯坦")

  # ========== 5. 输出 ==========
  print(
      "结构化结果 (JSON):\n",
      json.dumps(result.model_dump(), ensure_ascii=False, indent=2),
  )
  print("\n结构化结果 (对象):", result)
  print(f"\n姓名: {result.name}")
  print(f"出生年份: {result.birth_year}")
  print(f"国籍: {result.nationality}")
  print(f"研究领域: {', '.join(result.fields)}")


if __name__ == "__main__":
  main()
