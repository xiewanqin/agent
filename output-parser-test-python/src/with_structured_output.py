"""
LangChain 1.x 结构化输出（对应 output-parser-test/src/with-structured-output.mjs）

DashScope OpenAI 兼容模式：若用 json 类 response_format，接口要求 messages 里必须出现「json」字样，
否则会 400：'messages' must contain the word 'json' in some form ...

可选环境变量 STRUCTURED_OUTPUT_METHOD=function_calling 走工具形态，减少对该限制的依赖。
"""
import json
import os

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


class Scientist(BaseModel):
    name: str = Field(description="科学家的全名")
    birth_year: int = Field(description="出生年份")
    nationality: str = Field(description="国籍")
    fields: list[str] = Field(description="研究领域列表")


_method = os.getenv("STRUCTURED_OUTPUT_METHOD", "").strip().lower() or None
if _method == "function_calling":
    structured_model = model.with_structured_output(Scientist, method="function_calling")
else:
    # 默认 json_schema；DashScope 等若仍报 json 关键字错误，可设 STRUCTURED_OUTPUT_METHOD=function_calling
    structured_model = model.with_structured_output(Scientist)


def main() -> None:
    # 必须包含单词 json（DashScope 对 response_format=json_object 的校验）
    prompt = (
        "介绍一下爱因斯坦。"
        "请严格按 schema 输出，并以 json 形式给出 name、birth_year、nationality、fields。"
    )

    result: Scientist = structured_model.invoke(prompt)

    print("原始结果:", result)
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
