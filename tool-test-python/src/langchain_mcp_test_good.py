import asyncio
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

load_dotenv()

MCP_SERVER_PATH = "/Users/xiewq/web/agent/tool-test/src/my-mcp-server.py"


async def get_resource_text_from_session(session) -> str:
  """从 MCP session 读取所有资源的文本并拼成一段字符串。"""
  resources = await session.list_resources()
  parts = []
  for r in resources.resources:
    content = await session.read_resource(r.uri)
    for item in content.contents:
      if getattr(item, "text", None):
        parts.append(item.text)
  return "\n".join(parts)

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
      f"openai:{os.getenv('MODEL_NAME')}",
      api_key=os.getenv("OPENAI_API_KEY"),
      base_url=os.getenv("OPENAI_BASE_URL"),
      temperature=0,
  )

  client = MultiServerMCPClient(
      {
          "my-mcp-server": {
              "command": "python",
              "args": [MCP_SERVER_PATH],
              "transport": "stdio",
          },
          # "amap-maps-streamableHTTP": {
          #     "url": f"https://mcp.amap.com/mcp?key={os.getenv('AMAP_MAPS_API_KEY')}",
          #     "transport": "http",
          # },
          # "filesystem": {
          #     "command": "npx",
          #     "args": [
          #         "-y",
          #         "@modelcontextprotocol/server-filesystem",
          #         *[p.strip()
          #           for p in os.getenv("ALLOWED_PATHS", "").split(",") if p.strip()],
          #     ],
          #     "transport": "stdio",
          # },
          # "chrome-devtools": {
          #     "command": "npx",
          #     "args": [
          #         "-y",
          #         "chrome-devtools-mcp@latest",
          #     ],
          #     "transport": "stdio",
          # },
      }
  )

  async def load_mcp_resources():
    """自动加载所有 MCP resources。get_resources() 返回 list[Blob]，Blob 已包含内容。"""
    resources = await client.get_resources()
    resources_text = [blob.as_string()
                      for blob in resources if blob.as_string().strip()]
    return "\n".join(resources_text)

  # async with (
  #     client.session("my-mcp-server") as my_session,
  #     client.session("amap-maps-streamableHTTP") as amap_session,
  #     client.session("filesystem") as fs_session,
  #     client.session("chrome-devtools") as chrome_session,
  # ):
  #   log_info("📦 正在加载 MCP 工具...")
  #   my_tools = await load_mcp_tools(my_session)
  #   amap_tools = await load_mcp_tools(amap_session)
  #   fs_tools = await load_mcp_tools(fs_session)
  #   chrome_tools = await load_mcp_tools(chrome_session)
  # tools = my_tools + amap_tools + fs_tools + chrome_tools
  tools = await client.get_tools()
  log_success(f"✅ 已加载 {len(tools)} 个工具: {[t.name for t in tools]}")

  # 加载资源内容作为 system_prompt（只从 my-mcp-server 读取）
  log_info("📚 正在加载 MCP 资源...")
  # resource_content = await get_resource_text_from_session(my_session)
  #  if resource_content:
  #     resource_content = (
  #         "以下是你可参考的文档内容，请仅根据这些内容或工具返回的结果回答，不要编造。若文档或工具结果中无相关内容，请明确说明「文档/工具中未提及」。\n\n"
  #         + resource_content
  #     )
  resource_content = await load_mcp_resources()
  log_success(f"✅ 已加载资源内容 ({len(resource_content)} 字符)")

  # 使用 create_agent 创建 agent (LangChain 1.0 新特性)
  log_info("🤖 正在创建 Agent...")
  graph = create_agent(
      model=model,
      tools=tools,
      system_prompt=resource_content if resource_content else None,
  )
  log_success("✅ Agent 创建完成")

  async def run_agent(query: str, stream: bool = True):
    log_info(f"\n💬 用户查询: {query}")

    inputs = {
        "messages": [
            {"role": "user", "content": query}
        ]
    }

    if stream:
        # 流式模式：实时展示每步工具调用过程
      log_info("⏳ Agent 正在处理（流式）...")
      result = None
      async for chunk in graph.astream(inputs, stream_mode="values"):
        msgs = chunk.get("messages", [])
        if not msgs:
          continue
        last = msgs[-1]

        # model 节点：AI 决定调用哪些工具
        if hasattr(last, "tool_calls") and last.tool_calls:
          for tc in last.tool_calls:
            args_str = ", ".join(f"{k}={v}" for k, v in tc["args"].items())
            log_info(f"🤖 AI 决定调用: [{tc['name']}]  参数: {args_str}")

        # tools 节点：工具执行完毕，返回结果
        elif hasattr(last, "name") and hasattr(last, "tool_call_id"):
          preview = str(last.content)[:100].replace("\n", " ")
          log_success(
              f"🔧 [{
                  last.name}] 返回: {preview}{
                  '...' if len(
                      str(
                          last.content)) > 100 else ''}")

        result = chunk
    else:
      # 非流式模式：直接等待最终结果，不展示中间过程
      log_info("⏳ Agent 正在处理...")
      result = await graph.ainvoke(inputs)

    # 提取最终回复：必须是「没有 tool_calls 的 AIMessage」，避免误把 ToolMessage 当最终回复
    # 对话顺序: HumanMessage -> AIMessage(tool_calls) -> ToolMessage -> AIMessage(最终文字)
    if "messages" in result:
      msgs = result["messages"]
      final_ai_msg = None
      for m in reversed(msgs):
        if isinstance(m, AIMessage) and not (getattr(m, "tool_calls", None)):
          final_ai_msg = m
          break
      if final_ai_msg and getattr(final_ai_msg, "content", None):
        log_success(f"\n✨ AI 最终回复:\n{final_ai_msg.content}\n")
        return final_ai_msg.content
      last_message = msgs[-1]
      if hasattr(last_message, "content"):
        log_success(f"\n✨ AI 回复:\n{last_message.content}\n")
        return last_message.content
      log_success(f"\n✨ AI 回复:\n{result}\n")
      return str(result)
    else:
      log_success(f"\n✨ AI 回复:\n{result}\n")
      return str(result)

    # await run_agent("北京南站附近的5个酒店，以及去的路线，路线规划生成文档保存到
    # /Users/xiewq/web/agent/tool-test-python 的一个 md 文件")
    # await run_agent("北京南站附近的酒店，最近的 3 个酒店，拿到酒店图片，打开浏览器，展示每个酒店的图片，每个 tab 一个
    # url 展示，并且在把那个页面标题改为酒店名")
    # await run_agent("查一下用户 002 的信息")

  await run_agent("MCP Server 的使用指南是什么")


if __name__ == "__main__":
  asyncio.run(main())
