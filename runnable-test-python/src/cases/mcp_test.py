import os
import asyncio
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnableBranch, RunnablePassthrough, RunnableSequence
# import chromadb  # 如果需要其他功能

# 加载环境变量
load_dotenv()

MCP_SERVER_PATH = "/Users/xiewq/web/agent/tool-test/src/my-mcp-server.py"

# 初始化模型
model = ChatOpenAI(
    model="qwen-plus",
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    temperature=0.7
)

# 初始化MCP客户端


async def initialize_mcp_client():
  mcp_client = MultiServerMCPClient({
      "amap-maps-streamableHTTP": {
          "url": f"https://mcp.amap.com/mcp?key={os.getenv('AMAP_MAPS_API_KEY')}",
          "transport": "http",
      },
      "chrome-devtools": {
          "command": "npx",
          "args": ["-y", "chrome-devtools-mcp@latest"],
          "transport": "stdio",
      }
  })

  # 获取工具
  tools = await mcp_client.get_tools()
  return mcp_client, tools

# 创建提示模板


def create_prompt():
  return ChatPromptTemplate.from_messages([
      ("system", "你是一个可以调用 MCP 工具的智能助手。"),
      MessagesPlaceholder(variable_name="messages"),
  ])


# 工具执行器


class ToolExecutor:
  def __init__(self, tools: List):
    self.tools = {tool.name: tool for tool in tools}

  async def execute(self, state: Dict) -> List[ToolMessage]:
    response = state["response"]
    tool_results = []

    if hasattr(response, 'tool_calls') and response.tool_calls:
      for tool_call in response.tool_calls:
        tool_name = tool_call.get("name")
        if tool_name in self.tools:
          tool = self.tools[tool_name]
          tool_args = tool_call.get("args", {})

          # 调用工具
          tool_result = await tool.ainvoke(tool_args)

          # 处理返回结果
          if isinstance(tool_result, str):
            content_str = tool_result
          elif hasattr(tool_result, 'text'):
            content_str = tool_result.text
          else:
            content_str = json.dumps(tool_result, ensure_ascii=False)

          tool_results.append(ToolMessage(
              content=content_str,
              tool_call_id=tool_call.get("id")
          ))

    return tool_results

# 创建代理步骤链


def create_agent_chain(model_with_tools, prompt, tools):
  tool_executor = ToolExecutor(tools)

  # 定义Runnable分支
  def check_tool_calls(state: Dict) -> bool:
    response = state.get("response")
    if not response:
      return True
    return not (hasattr(response, 'tool_calls') and response.tool_calls)

  async def handle_no_tools(state: Dict) -> Dict:
    messages = state.get("messages", [])
    response = state.get("response")
    new_messages = messages + [response]

    # 获取最终内容
    final_content = response.content if hasattr(response, 'content') else str(response)

    return {
        **state,
        "messages": new_messages,
        "done": True,
        "final": final_content
    }

  async def log_tool_calls(state: Dict) -> Dict:
    messages = state.get("messages", [])
    response = state.get("response")
    new_messages = messages + [response]

    print(f"\033[94m🔍 检测到 {len(response.tool_calls)} 个工具调用\033[0m")
    print(
        f"\033[94m🔍 工具调用: {', '.join([tc.get('name') for tc in response.tool_calls])}\033[0m")

    return {
        **state,
        "messages": new_messages
    }

  # assign(toolMessages=...) 会把本函数的返回值直接写入 state["toolMessages"]，必须是 list，不能返回整份 state
  async def execute_tools(state: Dict) -> List[ToolMessage]:
    return await tool_executor.execute(state)

  async def finalize_tool_execution(state: Dict) -> Dict:
    messages = state.get("messages", [])
    tool_messages = state.get("toolMessages", [])

    return {
        **state,
        "messages": messages + tool_messages,
        "done": False
    }

  # 构建链
  agent_step_chain = RunnableSequence(
      RunnablePassthrough.assign(
          response=prompt | model_with_tools
      ),
      RunnableBranch(
          (check_tool_calls, RunnableLambda(handle_no_tools)),
          RunnableSequence(
              RunnableLambda(log_tool_calls),
              RunnablePassthrough.assign(toolMessages=RunnableLambda(execute_tools)),
              RunnableLambda(finalize_tool_execution)
          )
      )
  )

  return agent_step_chain

# 运行代理


async def run_agent_with_tools(query: str, max_iterations: int = 30):
  # 初始化MCP客户端
  mcp_client, tools = await initialize_mcp_client()

  # 绑定工具到模型
  model_with_tools = model.bind_tools(tools)

  # 创建提示模板
  prompt = create_prompt()

  # 创建代理链
  agent_chain = create_agent_chain(model_with_tools, prompt, tools)

  # 初始状态
  state = {
      "messages": [HumanMessage(content=query)],
      "done": False,
      "final": None,
      "response": None
  }

  for i in range(max_iterations):
    print(f"\033[92m⏳ 正在等待 AI 思考... (第 {i + 1} 轮)\033[0m")

    try:
      # 执行一轮代理步骤
      state = await agent_chain.ainvoke(state)

      if state.get("done"):
        print(f"\n✨ AI 最终回复:\n{state['final']}\n")
        return state["final"]
    except Exception as e:
      print(f"执行出错: {e}")
      break

  # 如果达到最大迭代次数，返回最后一条消息
  final_message = state["messages"][-1]
  final_content = final_message.content if hasattr(
      final_message, 'content') else str(final_message)
  print(f"\n✨ 达到最大迭代次数，最后回复:\n{final_content}\n")
  return final_content

# 主函数


async def main():
  query = "北京南站附近的酒店，最近的 3 个酒店，拿到酒店图片，打开浏览器，展示每个酒店的图片，每个 tab 一个 url 展示，并且在把那个页面标题改为酒店名"

  result = await run_agent_with_tools(query)
  print(f"最终结果: {result}")

if __name__ == "__main__":
  asyncio.run(main())
