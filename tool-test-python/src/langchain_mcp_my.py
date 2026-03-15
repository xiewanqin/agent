import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
# from langchain_core.messages import SystemMessage, HumanMessage
import asyncio

load_dotenv()

model = init_chat_model(
    "openai:qwen-plus",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)


async def main():
  mcp_client = MultiServerMCPClient({
      "my-mcp-server": {
          "command": "python",
          "args": [
              "/Users/xiewq/web/agent/tool-test-python/src/my-mcp-server.py"
          ],
          "transport": "stdio",
      }
  })

  tools = await mcp_client.get_tools()

  # 列出资源
  res = await mcp_client.get_resources()
  print(res)
  graph = create_agent(
      model=model,
      tools=tools,
      # system_prompt=resource_content,
  )

  response = await graph.ainvoke({
      "messages": [
          {"role": "user", "content": "查一下用户 002 的信息"}
      ]
  })


if __name__ == "__main__":
  asyncio.run(main())
