"""
简洁版：仅 astream + JsonOutputToolsParser(partial=True)，流式预览 write_file 的 content。

运行：cd .../src/test && uv run python mini_cursor_astream_parser_simple.py

================================================================================
【通俗版：这段代码在干什么？】
================================================================================

可以把 Agent 想成「会动脑的客服 + 几只手（工具）」：
- 用户提需求（QUERY / CASE1）
- 模型一边想一边往外吐字（流式）；有时直接说话，有时说「我要调用 write_file」
  并把「写哪、写什么」放在一段结构化 JSON 里（工具调用），不是普通聊天文字。

问题：流式时 JSON 是一段段到的，像「先看到 { 再看到 file_path 再看到 content 的前 100 字…」。
所以我们：
1. 把每一小片模型输出拼起来（pending），像拼拼图；
2. 用 JsonOutputToolsParser(..., partial=True) 不断问：「以目前已拼好的部分，能不能
   已经看出要写什么文件、内容已经有多少？」能就看 write_file 的 content，多出来的
   新字就打印到屏幕上 → 你看到的「流式预览」；
3. 模型说完这一轮、工具真的执行完，会进来一条 ToolMessage（工具执行结果）。
   这时要把拼图清空（pending = None），否则下一轮模型说话会和上一轮粘在一起。

astream 会交替给你三类东西（stream_mode 里写了三个）：
- messages：模型刚流出来的「一小片」→ 用来拼 pending、解析、预览或打印普通文字；
- updates：图里某个节点干完活了（例如工具跑完了）→ 我们只关心里面有没有 ToolMessage，
  有就清空累积；
- values：当前整份对话状态快照 → 循环结束后用最后一条消息类型打个尾。

_wf_args：从解析器给出的「一条工具调用」字典里，取出路径和正文（兼容 file_path / filePath）。
_out_text：模型在正常聊天、不是工具 JSON 时，把这一小片的可见文字打到屏幕上。

================================================================================
"""
from __future__ import annotations

import asyncio
import json
import os
import sys

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.output_parsers.openai_tools import JsonOutputToolsParser
from langchain_core.outputs import ChatGeneration
from langchain_openai import ChatOpenAI

from all_tool import execute_command, list_directory, read_file, write_file

load_dotenv()

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME", "qwen-plus"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)
agent = create_agent(
    model=model,
    tools=[read_file, write_file, execute_command, list_directory],
    system_prompt=(
        f"项目管理助手，cwd={os.getcwd()}；工具: read/write/execute_command/list_directory。"
        "execute_command 若带 working_directory 则不要在 command 里 cd。"
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

QUERY = CASE1


def _wf_args(tc: dict) -> tuple[str | None, str | None]:
  """从 JsonOutputToolsParser 解析出的单条工具调用里取出 write_file 的路径与正文。

  tc 形态类似: {"type": "write_file", "args": {...}, ...}
  - Python 工具参数名是 file_path，部分网关/模型会返回驼峰 filePath，故两种都读。
  - content 即要写入的文件内容；流式阶段会从不完整 JSON 逐渐变长，供上面增量打印。
  """
  # 工具调用的参数字典（流式解析时可能字段逐渐齐全）
  a = tc.get("args") or {}
  # 目标路径：与 all_tool.write_file 的 file_path 对齐；兼容模型返回 filePath
  p = a.get("file_path") or a.get("filePath")
  # 文件正文；partial 解析过程中会从短变长
  c = a.get("content")
  # 统一成 str，None 表示这一帧里还没有 content 字段
  return p, (str(c) if c is not None else None)


def _out_text(msg: AIMessage) -> None:
  c = msg.content
  if c:
    sys.stdout.write(c if isinstance(c, str) else json.dumps(c, ensure_ascii=False))
    sys.stdout.flush()


async def run(query: str) -> None:
  inp = {"messages": [HumanMessage(content=query)]}
  pending: AIMessage | None = None
  parser = JsonOutputToolsParser()
  printed: dict[str, int] = {}
  last_state: dict | None = None

  async for mode, payload in agent.astream(
      inp, stream_mode=["messages", "updates", "values"]
  ):
    if mode == "messages":
      print(f"mode: {mode}")

      msg, _meta = payload
      print(f"msg: {msg} \n metadata: {_meta}")
      if not isinstance(msg, AIMessage):
        continue
      pending = msg if pending is None else pending + msg
      try:
        tools = parser.parse_result(
            [ChatGeneration(message=pending)], partial=True
        )
      except Exception:
        tools = None
      if tools:
        for tc in tools:
          if tc.get("type") != "write_file":
            continue
          fp, text = _wf_args(tc)
          if not text:
            continue
          tid = tc.get("id") or fp or "default"
          if tid not in printed:
            printed[tid] = 0
            print(f'\n[write_file] "{fp}" 流式预览\n', end="")
          prev = printed[tid]
          if len(text) > prev:
            sys.stdout.write(text[prev:])
            sys.stdout.flush()
            printed[tid] = len(text)
      else:
        _out_text(msg)

    elif mode == "updates":
      for u in payload.values():
        if not isinstance(u, dict):
          continue
        for m in u.get("messages") or []:
          if isinstance(m, ToolMessage):
            pending = None
            printed.clear()

    else:
      last_state = payload

  print("\n--- done ---")
  if last_state and (msgs := last_state.get("messages")):
    print("last:", type(msgs[-1]).__name__)


if __name__ == "__main__":
  asyncio.run(run(QUERY))
