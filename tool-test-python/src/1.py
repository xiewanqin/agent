import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
import asyncio
from pathlib import Path

load_dotenv()

model = ChatOpenAI(
    model_name=os.getenv("MODEL_NAME", "qwen-coder-turbo"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)


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
model_with_tools = model.bind_tools(tools)

messages = [
    SystemMessage(content="""你是一个代码助手，可以使用工具读取文件并解释代码。

工作流程：
1. 用户要求读取文件时，立即调用 read_file 工具
2. 等待工具返回文件内容
3. 基于文件内容进行详细的分析和解释，说明做了哪些事

可用工具：
- read_file: 读取文件内容（使用此工具来获取文件内容）
"""),
    HumanMessage(content='请读取 ./src/1.py 文件内容并解释代码')
]


async def main():
  print('[步骤1] 第一次调用 AI 模型...')
  response = await model_with_tools.ainvoke(messages)
  print('[步骤1完成] AI 返回了响应')

  messages.append(response)

  max_iterations = 10
  iteration_count = 0

  while response.tool_calls and iteration_count < max_iterations:
    iteration_count += 1

    print(f"\n[步骤2-{iteration_count}] 检测到 {len(response.tool_calls)} 个工具调用")

    tool_results = await asyncio.gather(*[
        execute_tool(tool_call) for tool_call in response.tool_calls
    ])

    for tool_call, result in zip(response.tool_calls, tool_results):
      messages.append(
          ToolMessage(
              content=result,
              tool_call_id=tool_call["id"]
          )
      )

    print(f"[步骤3-{iteration_count}] 将工具结果发送给 AI，等待最终回复...")
    response = await model_with_tools.ainvoke(messages)
    messages.append(response)

    if response.tool_calls:
      print(f"[步骤3-{iteration_count}完成] AI 又返回了 {len(response.tool_calls)} 个工具调用，继续循环...")
    else:
      print(f"[步骤3-{iteration_count}完成] AI 返回了最终回复，退出循环")

  if iteration_count >= max_iterations and response.tool_calls:
    print(f"\n⚠️ 警告: 达到最大迭代次数 ({max_iterations})，强制退出循环")

  print('\n========== 最终回复 ==========')
  print(response.content)


async def execute_tool(tool_call):
  tool_name = tool_call["name"]
  tool_args = tool_call["args"]

  for tool in tools:
    if tool.name == tool_name:
      print(f"  [执行工具] {tool_name}({tool_args})")
      try:
        result = await tool.ainvoke(tool_args)
        return result
      except Exception as e:
        return f"错误: {str(e)}"

  return f"错误: 找不到工具 {tool_name}"

if __name__ == "__main__":
  asyncio.run(main())
