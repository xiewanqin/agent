"""
对应 output-parser-test/src/test/mini-cursor.mjs

手工 Agent 循环：stream + JsonOutputToolsParser 增量解析 + write_file 内容流式预览。
工具定义见同目录 all_tool.py（参数为 snake_case：file_path、working_directory）。
"""
from __future__ import annotations

import asyncio
import json
import os
import sys

from dotenv import load_dotenv
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
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

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME", "qwen-plus"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)

tools = [read_file, write_file, execute_command, list_directory]
model_with_tools = model.bind_tools(tools)


def _write_file_args(tool_call: dict) -> tuple[str | None, str | None]:
    """兼容 OpenAI 可能返回的 camelCase / Python 工具的 snake_case。"""
    args = tool_call.get("args") or {}
    path = args.get("file_path") or args.get("filePath")
    content = args.get("content")
    if content is not None:
        content = str(content)
    return path, content


async def run_agent_with_tools(query: str, max_iterations: int = 30) -> str | None:
    history = InMemoryChatMessageHistory()

    history.add_message(
        SystemMessage(
            content=f"""你是一个项目管理助手，使用工具完成任务。

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
        )
    )
    history.add_message(HumanMessage(content=query))

    tool_parser = JsonOutputToolsParser()

    for _ in range(max_iterations):
        print("\n⏳ 正在等待 AI 思考...")

        messages = await history.aget_messages()
        stream = model_with_tools.astream(messages)

        full_ai_message = None
        printed_lengths: dict[str, int] = {}

        print("\n🚀 Agent 开始思考并生成流...\n")

        async for chunk in stream:
            full_ai_message = chunk if full_ai_message is None else full_ai_message + chunk

            parsed_tools: list | None = None
            try:
                parsed_tools = tool_parser.parse_result(
                    [ChatGeneration(message=full_ai_message)],
                    partial=True,
                )
            except Exception:
                pass

            if parsed_tools:
                for tool_call in parsed_tools:
                    if tool_call.get("type") != "write_file":
                        continue
                    fp, content = _write_file_args(tool_call)
                    if not content:
                        continue
                    tool_id = tool_call.get("id") or fp or "default"
                    prev = printed_lengths.get(tool_id, 0)
                    if tool_id not in printed_lengths:
                        printed_lengths[tool_id] = 0
                        print(f'\n[工具调用] write_file("{fp}") - 开始写入（流式预览）\n')
                    if len(content) > prev:
                        sys.stdout.write(content[prev:])
                        sys.stdout.flush()
                        printed_lengths[tool_id] = len(content)
            else:
                if chunk.content:
                    if isinstance(chunk.content, str):
                        sys.stdout.write(chunk.content)
                    else:
                        sys.stdout.write(json.dumps(chunk.content, ensure_ascii=False))
                    sys.stdout.flush()

        assert full_ai_message is not None
        history.add_message(full_ai_message)
        print("\n✅ 消息已完整存入历史")

        tool_calls = getattr(full_ai_message, "tool_calls", None) or []
        if not tool_calls:
            print(f"\n✨ AI 最终回复:\n{full_ai_message.content}\n")
            return (
                full_ai_message.content
                if isinstance(full_ai_message.content, str)
                else str(full_ai_message.content)
            )

        for tc in tool_calls:
            if isinstance(tc, dict):
                name, args, tc_id = tc.get("name"), tc.get("args") or {}, tc.get("id")
            else:
                name = getattr(tc, "name", None)
                args = getattr(tc, "args", None) or {}
                tc_id = getattr(tc, "id", None)
            found = next((t for t in tools if t.name == name), None)
            if found:
                result = await found.ainvoke(args)
                history.add_message(
                    ToolMessage(content=str(result), tool_call_id=tc_id)
                )

    final_messages = await history.aget_messages()
    last = final_messages[-1]
    return getattr(last, "content", None)


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


async def _main() -> None:
    await run_agent_with_tools(CASE1)


if __name__ == "__main__":
    try:
        asyncio.run(_main())
    except Exception as e:
        print(f"\n❌ 错误: {e}\n", file=sys.stderr)
        raise
