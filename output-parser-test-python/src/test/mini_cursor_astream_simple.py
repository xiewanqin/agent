"""
简洁版：仅 create_agent + graph.astream（无 astream_events、无 JsonOutputToolsParser）。

默认任务很短；要大任务可改 QUERY 或：
  QUERY="$(cat task.txt)" uv run python mini_cursor_astream_simple.py
  # 或在本文件里把 QUERY 换成 mini_cursor_create_agent.CASE1 那段字符串
"""
from __future__ import annotations

import asyncio
import json
import os
import sys

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

from all_tool import execute_command, list_directory, read_file, write_file

load_dotenv()

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
    system_prompt=(
        f"你是命令行助手，工作目录: {os.getcwd()}。\n"
        "可用工具: read_file, write_file, execute_command, list_directory。\n"
        "execute_command 若传 working_directory，不要在 command 里再 cd。"
    ),
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

# 默认短任务；需要完整 Todo 案例可从 mini_cursor_create_agent 复制 CASE1
QUERY = CASE1


async def main() -> None:
  inp = {"messages": [HumanMessage(content=QUERY)]}
  last: dict | None = None

  async for mode, payload in agent.astream(inp, stream_mode=["messages", "values"]):
    if mode == "messages":
      msg, _meta = payload
      if not isinstance(msg, AIMessage):
        continue
      c = msg.content
      if not c:
        continue
      sys.stdout.write(c if isinstance(c, str) else json.dumps(c, ensure_ascii=False))
      sys.stdout.flush()
    else:
      last = payload

  print("\n\n--- 结束 ---")
  if last and (msgs := last.get("messages")):
    tail = msgs[-1]
    print("最后一条:", type(tail).__name__, getattr(tail, "content", "")[:200])


if __name__ == "__main__":
  asyncio.run(main())
