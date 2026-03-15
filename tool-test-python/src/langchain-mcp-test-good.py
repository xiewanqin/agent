import asyncio
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

load_dotenv()

MCP_SERVER_PATH = "/Users/xiewq/web/agent/tool-test/src/my-mcp-server.py"

try:
  from colorama import Back, Style, init

  init(autoreset=True)

  def log_info(msg: str):
    print(Back.CYAN + msg)

  def log_success(msg: str):
    print(Back.GREEN + msg)

except ImportError:

  def log_info(msg: str):
    print(msg)

  def log_success(msg: str):
    print(msg)


async def main():
  # 使用 init_chat_model (LangChain 1.0 推荐方式)
  model = init_chat_model(
      f"openai:{os.getenv['MODEL_NAME']}",
      api_key=os.getenv["OPENAI_API_KEY"],
      base_url=os.getenv["OPENAI_BASE_URL"],
      temperature=0,
  )

  client = MultiServerMCPClient(
      {
          "my-mcp-server": {
              "command": "python",
              "args": [MCP_SERVER_PATH],
              "transport": "stdio",
          }
      }
  )

  async with client.session("my-mcp-server") as session:
    log_info("📦 正在加载 MCP 工具...")
    tools = await load_mcp_tools(session)
    log_success(f"✅ 已加载 {len(tools)} 个工具: {[t.name for t in tools]}")

    # 加载资源内容作为 system_prompt
    log_info("📚 正在加载 MCP 资源...")
    resource_content = ""
    resources = await session.list_resources()
    for resource in resources.resources:
      content = await session.read_resource(resource.uri)
      for item in content.contents:
        if hasattr(item, "text"):
          resource_content += item.text
    log_success(f"✅ 已加载资源内容 ({len(resource_content)} 字符)")

    # 使用 create_agent 创建 agent (LangChain 1.0 新特性)
    log_info("🤖 正在创建 Agent...")
    graph = create_agent(
        model=model,
        tools=tools,
        system_prompt=resource_content if resource_content else None,
    )
    log_success("✅ Agent 创建完成")

    async def run_agent(query: str, stream: bool = False):
      """
      使用 create_agent 执行查询

      create_agent 的优势（LangChain 1.0 新特性）:
      1. 自动处理工具调用循环，无需手动编写循环逻辑
      2. 自动管理消息历史（HumanMessage, AIMessage, ToolMessage）
      3. 自动判断何时停止（当 AI 不再调用工具时）
      4. 支持流式输出，可以实时查看执行过程
      5. 内置错误处理和重试机制
      """
      log_info(f"\n💬 用户查询: {query}")

      inputs = {
          "messages": [
              {"role": "user", "content": query}
          ]
      }

      if stream:
        # 流式输出模式：实时查看 agent 执行过程
        # stream_mode="updates" 的 chunk 格式: {node_name: node_output}
        # create_agent 的节点名是 "model" 和 "tools"（不是 "agent"）
        log_info("⏳ Agent 正在流式处理...")
        result = None
        async for chunk in graph.astream(inputs, stream_mode="updates"):
          for node_name, node_output in chunk.items():
            if node_name == "model":
              log_info("🤖 Agent 正在思考...")
            elif node_name == "tools":
              log_info("🔧 正在执行工具...")
          result = chunk  # updates 模式最后一个 chunk 不包含完整 state

        # astream updates 模式拿不到完整最终结果，需要 ainvoke
        result = await graph.ainvoke(inputs)
      else:
        # 直接获取最终结果（推荐方式）
        log_info("⏳ Agent 正在处理...")
        result = await graph.ainvoke(inputs)

      # 提取最终回复（最后一条消息）
      # create_agent 返回的 result 包含完整的对话历史：
      # - HumanMessage (用户输入)
      # - AIMessage with tool_calls (AI 调用工具)
      # - ToolMessage (工具执行结果)
      # - AIMessage without tool_calls (AI 最终回复) <- 这是我们需要的
      if "messages" in result:
        last_message = result["messages"][-1]
        if hasattr(last_message, "content"):
          log_success(f"\n✨ AI 最终回复:\n{last_message.content}\n")
          return last_message.content
        else:
          log_success(f"\n✨ AI 回复:\n{result}\n")
          return str(result)
      else:
        log_success(f"\n✨ AI 回复:\n{result}\n")
        return str(result)

    # 执行查询
    # 方式 1: 直接获取结果（推荐）
    await run_agent("查一下用户 002 的信息")

    # 方式 2: 流式输出，可以看到每个步骤（model 思考 / tools 执行）
    await run_agent("查一下用户 002 的信息", stream=True)

    await run_agent("MCP Server 的使用指南是什么")


if __name__ == "__main__":
  asyncio.run(main())
