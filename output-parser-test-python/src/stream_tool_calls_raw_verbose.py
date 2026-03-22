"""
stream_tool_calls_raw 的「加长版」：双路取 args、可选 STREAM_FORCE_TOOL、末尾 json 校验。
极简对照 mjs 请用 stream_tool_calls_raw.py。
"""
import json
import os
import sys
from typing import List, Optional

from dotenv import load_dotenv
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()


class Scientist(BaseModel):
    name: str = Field(description="科学家的全名")
    birth_year: int = Field(description="出生年份")
    death_year: Optional[int] = Field(
        default=None, description="去世年份，如果还在世则不填"
    )
    nationality: str = Field(description="国籍")
    fields: List[str] = Field(description="研究领域列表")
    achievements: List[str] = Field(description="主要成就")
    biography: str = Field(description="简短传记")


def _extract_scientist_info_run(**kwargs: object) -> dict:
    return Scientist(**kwargs).model_dump()


def main() -> None:
    model = ChatOpenAI(
        model=os.getenv("MODEL_NAME"),
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        temperature=0,
        timeout=float(os.getenv("STREAM_REQUEST_TIMEOUT", "120")),
    )

    extract_scientist_info_tool = StructuredTool.from_function(
        name="extract_scientist_info",
        description="提取和结构化科学家的详细信息",
        func=_extract_scientist_info_run,
        args_schema=Scientist,
    )

    bind_kw: dict = {"parallel_tool_calls": False}
    if os.getenv("STREAM_FORCE_TOOL", "").strip() in (
        "1",
        "true",
        "yes",
        "required",
    ):
        bind_kw["tool_choice"] = "required"

    model_with_tools = model.bind_tools([extract_scientist_info_tool], **bind_kw)

    print("🌊 流式 Tool Calls（verbose）\n")
    if bind_kw.get("tool_choice"):
        print("（STREAM_FORCE_TOOL=1）\n")

    stream = model_with_tools.stream("详细介绍牛顿的生平和成就")
    print("📡 实时输出 arguments 片段:\n")

    buffer = ""

    def args_from_chunk(chunk: object) -> list[str]:
        out: list[str] = []
        tcc = getattr(chunk, "tool_call_chunks", None) or []
        for tc in tcc:
            if isinstance(tc, dict):
                frag = tc.get("args") or ""
            else:
                frag = getattr(tc, "args", None) or ""
            if frag:
                out.append(frag)
        ak = getattr(chunk, "additional_kwargs", None) or {}
        for tool_call in ak.get("tool_calls") or []:
            fn = tool_call.get("function") or {}
            frag = fn.get("arguments") or ""
            if frag:
                out.append(frag)
        return out

    for chunk in stream:
        for frag in args_from_chunk(chunk):
            print(frag, end="", flush=True)
            buffer += frag

    print("\n\n✅ 流式输出完成")

    try:
        parsed = json.loads(buffer)
        print(
            "\n🎯 解析结果:\n",
            json.dumps(parsed, ensure_ascii=False, indent=2),
        )
    except json.JSONDecodeError:
        print(
            "\n⚠️ 拼接结果不能解析为 JSON，长度=%d" % len(buffer),
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
