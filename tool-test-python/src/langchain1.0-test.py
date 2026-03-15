import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.tools import tool
import asyncio
from pathlib import Path

load_dotenv()

# model = ChatOpenAI(
#     model_name=os.getenv("MODEL_NAME", "qwen-plus"),
#     # api_key=os.getenv("OPENAI_API_KEY"),
#     temperature=0,
#     base_url=os.getenv("OPENAI_BASE_URL"),
# )

model = init_chat_model(
    # model='qwen-plus',
    # model_provider='openai',
    "openai:qwen-plus",
    # api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"))


@tool
async def read_file(file_path: str) -> str:
  """用此工具来读取文件内容。当用户要求读取文件、查看代码、分析文件内容时，调用此工具。输入文件路径（可以是相对路径或绝对路径）。"""
  try:
    path = Path(file_path)
    content = await asyncio.to_thread(path.read_text, encoding='utf-8')
    print(f"  [工具调用] read_file(\"{file_path}\") - 成功读取 {len(content)} 字节")
    return f"文件内容:\n{content}"
  except Exception as e:
    return f"错误: {str(e)}"

tools = [read_file]

system_prompt = """你是一个代码助手，可以使用工具读取文件并解释代码。

工作流程：
1. 用户要求读取文件时，立即调用 read_file 工具
2. 等待工具返回文件内容
3. 基于文件内容进行详细的分析和解释，说明做了哪些事

可用工具：
- read_file: 读取文件内容（使用此工具来获取文件内容）
"""

# 使用 create_agent 创建 agent graph
graph = create_agent(
    model=model,
    tools=tools,
    system_prompt=system_prompt,
)


async def main():
  print('[开始] 使用 create_agent 执行任务...')

  # 准备输入消息
  inputs = {
      "messages": [
          {"role": "user", "content": "请读取 ./src/langchain1.0-test.py 文件内容并解释代码"}
      ]
  }
  # 使用 ainvoke 直接获取最终结果（推荐方式）
  print('[执行中] Agent 正在处理...')
  result = await graph.ainvoke(inputs)

  print('\n========== 最终回复 ==========')
  # 为什么要提取最后一条消息？
  # create_agent 返回的 result 包含完整的对话历史，messages 列表包括：
  # 1. 用户输入的消息 (HumanMessage)
  # 2. AI 的中间回复 (AIMessage with tool_calls)
  # 3. 工具调用的结果 (ToolMessage)
  # 4. AI 的最终回复 (AIMessage without tool_calls) <- 这是我们需要的
  #
  # 我们只需要最后一条消息，因为那是 AI 的最终回复（不再调用工具）

  if "messages" in result:
    # 打印所有消息类型（用于调试）
    print(f'[调试] 消息总数: {len(result["messages"])}')
    for i, msg in enumerate(result["messages"]):
      msg_type = type(msg).__name__
      print(f'  [{i}] {msg_type}: {str(msg)[:50]}...' if len(
          str(msg)) > 50 else f'  [{i}] {msg_type}: {str(msg)}')

    # 提取最后一条消息（AI 的最终回复）
    last_message = result["messages"][-1]
    if hasattr(last_message, 'content'):
      print(f'\n[最终回复] {type(last_message).__name__}:')
      print(last_message.content)
    else:
      print('\n[最终回复] (无 content 属性):')
      print(result)
  else:
    print(result)

  # 如果需要流式输出，可以使用以下代码：
  # print('\n[流式执行] 开始流式处理...')
  # async for chunk in graph.astream(inputs, stream_mode="updates"):
  #   for node_name, node_output in chunk.items():
  #     if node_name == "agent":
  #       print(f"[Agent 节点] 处理中...")
  #     elif node_name == "tools":
  #       print(f"[Tools 节点] 执行工具...")
  #     elif node_name == "__end__":
  #       print(f"[完成] 处理完成")

if __name__ == "__main__":
  asyncio.run(main())
