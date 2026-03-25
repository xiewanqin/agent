import os
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient


# ==================== 加载环境变量 ====================
load_dotenv()

MCP_SERVER_PATH = "/Users/xiewq/web/agent/tool-test/src/my-mcp-server.py"

# ==================== 初始化模型 ====================
model = ChatOpenAI(
    model_name=os.getenv("MODEL_NAME", "qwen-coder-turbo"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)


# 初始化 MCP Client
mcp_client = MultiServerMCPClient(
    {
        "my-mcp-server": {
            "command": "python",
            "args": [MCP_SERVER_PATH],
            "transport": "stdio",
        },
    }
)


async def load_mcp_resources():
  """自动加载所有 MCP resources。get_resources() 返回 list[Blob]，Blob 已包含内容。"""
  resources = await mcp_client.get_resources()
  resources_text = [blob.as_string() for blob in resources if blob.as_string().strip()]
  return "\n".join(resources_text)


async def run_agent(query: str, max_iterations=30):

  # 获取 MCP tools
  tools = await mcp_client.get_tools()

  model_with_tools = model.bind_tools(tools)

  # 获取 MCP resources
  resource_content = await load_mcp_resources()

  messages = [
      SystemMessage(content=resource_content),
      HumanMessage(content=query)
  ]

  for i in range(max_iterations):

    print("⏳ AI 思考中...")

    response = await model_with_tools.ainvoke(messages)

    messages.append(response)

    tool_calls = getattr(response, "tool_calls", [])

    if not tool_calls:
      print("\n✨ 最终回答:\n")
      print(response.content)
      return response.content

    print(f"🔧 调用工具: {[t['name'] for t in tool_calls]}")

    for call in tool_calls:

      tool = next(t for t in tools if t.name == call["name"])

      result = await tool.ainvoke(call["args"])

      messages.append(
          ToolMessage(
              content=str(result),
              tool_call_id=call["id"],
          )
      )


async def main():

  await run_agent("查一下用户 002 的信息")

  await run_agent("MCP Server 的使用指南是什么")

  # await mcp_client.close()


asyncio.run(main())
