"""
对应 output-parser-test/src/structured-json-schema.mjs

用 Pydantic 定义结构，再用 model_json_schema() 生成 JSON Schema，
通过 ChatOpenAI 的 model_kwargs 传入 OpenAI 兼容的 response_format（json_schema）。
"""
import json
import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ConfigDict, Field

load_dotenv()


class Scientist(BaseModel):
    """与 zod scientistSchema + .strict() 对应：禁止多余字段。"""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="科学家的全名")
    birth_year: int = Field(description="出生年份")
    field: str = Field(description="主要研究领域")
    achievements: list[str] = Field(description="主要成就列表")


native_json_schema = Scientist.model_json_schema()

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME", "qwen-max"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
    model_kwargs={
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "scientist_info",
                "strict": True,
                "schema": native_json_schema,
            },
        }
    },
)


def main() -> None:
    print("🧪 测试原生 JSON Schema 模式...\n")

    res = model.invoke(
        [
            SystemMessage(content="你是一个信息提取助手，请直接返回 JSON 数据。"),
            HumanMessage(content="介绍一下杨振宁"),
        ]
    )

    text = res.content if isinstance(res.content, str) else str(res.content)
    print("\n✅ 收到响应 (纯净 JSON):")
    print(text)

    data = json.loads(text)
    print("\n📋 解析后的对象:")
    print(data)


if __name__ == "__main__":
    main()
