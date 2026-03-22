"""
与 mini_cursor.py 并列：create_agent + 流式消费。

- run_with_astream：astream(messages / updates / values)
  在 messages 流上累积 AIMessageChunk，用 JsonOutputToolsParser(partial=True) 增量解析
  tool_calls JSON，与 mini_cursor.py 相同方式流式预览 write_file 的 content。
  在 updates 里一旦出现 ToolMessage，清空累积（表示本轮模型已结束、工具已跑，下一轮
  模型流重新计数）。
- run_with_astream_events：仅把 on_chat_model_stream 的 chunk.content 打到终端；
  工具参数多半在 tool_call 流里，events 这一路仍不做 write_file 正文预览（要做得再
  对 chunk 做同样的 parser 累积，易与多 Runnable 混淆）。

运行：
  uv run python mini_cursor_create_agent.py           # 默认 astream（含 write_file 预览）
  uv run python mini_cursor_create_agent.py events    # 仅 astream_events
  uv run python mini_cursor_create_agent.py both      # 两种各跑一遍（耗双倍 token）
"""
from __future__ import annotations

import asyncio
import json
import os
import sys

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.output_parsers.openai_tools import JsonOutputToolsParser
from langchain_core.outputs import ChatGeneration
from langchain_openai import ChatOpenAI

from all_tool import (
    execute_command,
    list_directory,
    read_file,
    write_file,
)

load_dotenv()

SYSTEM_PROMPT = f"""你是一个项目管理助手，使用工具完成任务。

当前工作目录: {os.getcwd()}

工具：
1. read_file: 读取文件
2. write_file: 写入文件
3. execute_command: 执行命令（支持 working_directory 参数）
4. list_directory: 列出目录

重要规则 - execute_command：
- working_directory 参数会自动切换到指定目录
- 当使用 working_directory 时，绝对不要在 command 中使用 cd
- 错误示例: {{ command: "cd react-todo-app && pnpm install", working_directory: "react-todo-app" }}
- 正确示例: {{ command: "pnpm install", working_directory: "react-todo-app" }}

重要规则 - write_file：
- 当写入 React 组件文件（如 App.tsx）时，如果存在对应的 CSS 文件（如 App.css），在其他 import 语句后加上这个 css 的导入
"""

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME", "qwen-plus"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)

tools = [read_file, write_file, execute_command, list_directory]

agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
)

CASE1 = """创建一个功能丰富的 React TodoList 应用：

1. 创建项目：echo -e "n\nn" | pnpm create vite react-todo-app --template react-ts
2. 修改 src/App.tsx，实现完整功能的 TodoList：
 - 添加、删除、编辑、标记完成
 - 分类筛选（全部/进行中/已完成）
 - 统计信息显示
 - localStorage 数据持久化
3. 添加复杂样式：
 - 渐变背景（蓝到紫）
 - 卡片阴影、圆角
 - 悬停效果
4. 添加动画：
 - 添加/删除时的过渡动画
 - 使用 CSS transitions
5. 列出目录确认

注意：使用 pnpm，功能要完整，样式要美观，要有动画效果

去掉 main.tsx 里的 index.css 导入

之后在 react-todo-app 项目中：
1. 使用 pnpm install 安装依赖
2. 使用 pnpm run dev 启动服务器
"""


def _brief_message(m: BaseMessage) -> str:
    if isinstance(m, ToolMessage):
        body = (m.content or "")[:200]
        return f"ToolMessage({m.name}): {body!r}..."
    if isinstance(m, AIMessage):
        tc = getattr(m, "tool_calls", None) or []
        if tc:
            names = [t.get("name", "?") if isinstance(t, dict) else getattr(t, "name", "?") for t in tc]
            return f"AIMessage tool_calls={names}"
        c = m.content
        if isinstance(c, str):
            return f"AIMessage text: {c[:120]!r}..."
        return f"AIMessage content={type(c).__name__}"
    return f"{type(m).__name__}: {str(m.content)[:120]}..."


def _write_chunk_content(chunk: BaseMessage) -> None:
    """把 LLM 流式 chunk 里的可见文本写到终端。"""
    c = chunk.content
    if not c:
        return
    if isinstance(c, str):
        sys.stdout.write(c)
    else:
        sys.stdout.write(json.dumps(c, ensure_ascii=False))
    sys.stdout.flush()


def _write_file_args_from_tool_call(tool_call: dict) -> tuple[str | None, str | None]:
    """与 mini_cursor.py 一致：兼容 file_path / filePath。"""
    args = tool_call.get("args") or {}
    path = args.get("file_path") or args.get("filePath")
    content = args.get("content")
    if content is not None:
        content = str(content)
    return path, content


async def run_with_astream(query: str) -> None:
    """LangGraph astream：messages（token/块）+ updates + values；messages 上支持 write_file 参数流式预览。"""
    print("\n========== create_agent + astream (messages / updates / values) ==========\n")

    inp = {"messages": [HumanMessage(content=query)]}
    last_values: dict | None = None

    # 当前这一轮模型调用的流式拼接（tool JSON 可能分多 chunk）
    pending_ai: AIMessage | None = None
    tool_parser = JsonOutputToolsParser()
    printed_lengths: dict[str, int] = {}

    async for mode, payload in agent.astream(
        inp,
        stream_mode=["messages", "updates", "values"],
    ):
        if mode == "messages":
            # payload = (message_chunk, metadata)
            msg, _meta = payload
            if not isinstance(msg, AIMessage):
                continue

            pending_ai = msg if pending_ai is None else pending_ai + msg

            parsed_tools: list | None = None
            try:
                parsed_tools = tool_parser.parse_result(
                    [ChatGeneration(message=pending_ai)],
                    partial=True,
                )
            except Exception:
                pass

            if parsed_tools:
                for tool_call in parsed_tools:
                    if tool_call.get("type") != "write_file":
                        continue
                    fp, wcontent = _write_file_args_from_tool_call(tool_call)
                    if not wcontent:
                        continue
                    tool_id = tool_call.get("id") or fp or "default"
                    prev = printed_lengths.get(tool_id, 0)
                    if tool_id not in printed_lengths:
                        printed_lengths[tool_id] = 0
                        print(f'\n[工具调用] write_file("{fp}") - 开始写入（流式预览）\n')
                    if len(wcontent) > prev:
                        sys.stdout.write(wcontent[prev:])
                        sys.stdout.flush()
                        printed_lengths[tool_id] = len(wcontent)
            else:
                # 尚未形成可解析的 tool_calls 时，只输出「本 chunk」的正文（避免重复打印）
                _write_chunk_content(msg)

        elif mode == "updates":
            print()
            for node_name, patch in payload.items():
                print(f"[updates] 节点: {node_name}")
                if isinstance(patch, dict) and "messages" in patch:
                    for m in patch["messages"]:
                        print(f"  + {_brief_message(m)}")
                        if isinstance(m, ToolMessage):
                            # 工具已执行完：下一轮模型流是新的一轮，必须清空 parser 累积
                            pending_ai = None
                            printed_lengths.clear()

        elif mode == "values":
            last_values = payload

    print("\n\n--- astream 结束 ---\n")
    if last_values and (msgs := last_values.get("messages")):
        last = msgs[-1]
        print("最后一条消息摘要:", _brief_message(last))
        if isinstance(last, AIMessage) and last.content and not (last.tool_calls or []):
            print("\n✨ 最终文本:\n", last.content)


async def run_with_astream_events(query: str) -> None:
    """Runnable astream_events v2：按事件类型观察模型流、工具开始/结束等。"""
    print("\n========== create_agent + astream_events (v2) ==========\n")

    inp = {"messages": [HumanMessage(content=query)]}

    interesting = {
        "on_chat_model_stream",
        "on_tool_start",
        "on_tool_end",
        "on_chain_error",
    }

    async for ev in agent.astream_events(inp, version="v2"):
        name = ev.get("event", "")
        if name not in interesting:
            continue

        if name == "on_chat_model_stream":
            data = ev.get("data") or {}
            chunk = data.get("chunk")
            if chunk is not None:
                _write_chunk_content(chunk)

        elif name == "on_tool_start":
            data = ev.get("data") or {}
            print(f"\n[tool_start] {ev.get('name')}: {data.get('input')}")

        elif name == "on_tool_end":
            data = ev.get("data") or {}
            out = data.get("output")
            preview = str(out)[:300]
            print(f"\n[tool_end] {ev.get('name')}: {preview!r}...")

        elif name == "on_chain_error":
            print("\n[error]", ev)

    print("\n\n--- astream_events 结束 ---\n")


async def main() -> None:
    mode = (sys.argv[1] if len(sys.argv) > 1 else "astream").lower()
    if mode == "events":
        await run_with_astream_events(CASE1)
    elif mode == "both":
        await run_with_astream(CASE1)
        await run_with_astream_events(CASE1)
    else:
        await run_with_astream(CASE1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ 错误: {e}\n", file=sys.stderr)
        raise
