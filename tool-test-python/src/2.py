from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

model = init_chat_model(
    "openai:qwen-plus",
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

system_prompt = """你是一个代码助手，可以使用工具读取文件并解释代码。

工作流程：
1. 用户要求读取文件时，立即调用 read_file 工具
2. 等待工具返回文件内容
3. 基于文件内容进行详细的分析和解释，说明做了哪些事

可用工具：
- read_file: 读取文件内容（使用此工具来获取文件内容）
"""

graph = create_agent(
    model=model,
    tools=tools,
    system_prompt=system_prompt,
)


async def main():
  print('[开始] 使用 create_agent 执行任务...')
  inputs = {
      "messages": [
          {"role": "user", "content": "请读取 ./src/2.py 文件内容并解释代码"}
      ]
  }
  result = await graph.ainvoke(inputs)
  print(result)

if __name__ == "__main__":
  asyncio.run(main())
