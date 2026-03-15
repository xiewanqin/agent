"""
演示 client.session() 的两种使用方式
"""
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

MCP_SERVER_PATH = "/Users/xiewq/web/agent/tool-test-python/src/my-mcp-server.py"


async def demo_with_session():
  """方式 1: 使用 session() - 推荐方式"""
  print("=" * 60)
  print("方式 1: 使用 client.session()")
  print("=" * 60)

  client = MultiServerMCPClient({
      "my-mcp-server": {
          "command": "python",
          "args": [MCP_SERVER_PATH],
          "transport": "stdio",
      }
  })

  # 使用 async with 创建持久会话
  async with client.session("my-mcp-server") as session:
    print("✅ 连接已建立，session 已创建")

    # 在同一个 session 中执行多个操作
    print("\n1️⃣ 获取工具...")
    tools = await load_mcp_tools(session)
    print(f"   获取到 {len(tools)} 个工具: {[t.name for t in tools]}")

    print("\n2️⃣ 列出资源...")
    resources = await session.list_resources()
    print(f"   找到 {len(resources.resources)} 个资源")

    print("\n3️⃣ 读取资源内容...")
    for resource in resources.resources:
      content = await session.read_resource(resource.uri)
      print(f"   资源 {resource.uri}: {len(content.contents)} 个内容项")

    print("\n4️⃣ 再次使用同一个 session...")
    # 可以继续使用同一个 session，无需重新建立连接
    tools_again = await load_mcp_tools(session)
    print(f"   再次获取工具: {len(tools_again)} 个")

    print("\n✅ 所有操作完成，即将退出 session...")

  print("✅ session 已关闭，连接已清理\n")


async def demo_without_session():
  """方式 2: 直接使用 client 方法 - 简化方式"""
  print("=" * 60)
  print("方式 2: 直接使用 client.get_tools()")
  print("=" * 60)

  client = MultiServerMCPClient({
      "my-mcp-server": {
          "command": "python",
          "args": [MCP_SERVER_PATH],
          "transport": "stdio",
      }
  })

  print("\n1️⃣ 第一次调用 get_tools()...")
  # 内部会创建临时 session，获取工具后关闭
  tools1 = await client.get_tools()
  print(f"   获取到 {len(tools1)} 个工具: {[t.name for t in tools1]}")
  print("   ⚠️  临时 session 已关闭")

  print("\n2️⃣ 第二次调用 get_tools()...")
  # 再次调用时，会创建新的临时 session
  tools2 = await client.get_tools()
  print(f"   获取到 {len(tools2)} 个工具: {[t.name for t in tools2]}")
  print("   ⚠️  临时 session 已关闭")

  print("\n3️⃣ 调用 get_resources()...")
  # 又会创建新的临时 session
  resources = await client.get_resources()
  print(f"   获取到资源: {resources}")
  print("   ⚠️  临时 session 已关闭")

  print("\n⚠️  注意：每次调用都创建了新连接，有性能开销\n")


async def main():
  print("\n" + "🔍 client.session() 演示".center(60, "=") + "\n")

  # 演示方式 1
  await demo_with_session()

  # 演示方式 2
  await demo_without_session()

  print("\n" + "=" * 60)
  print("总结:")
  print("=" * 60)
  print("""
方式 1 (session):
  ✅ 一次连接，多次使用
  ✅ 性能更好
  ✅ 支持资源操作
  ✅ 自动资源管理

方式 2 (get_tools/get_resources):
  ✅ 使用简单
  ⚠️  每次调用都创建新连接
  ⚠️  性能开销较大
  ⚠️  不适合频繁调用
    """)


if __name__ == "__main__":
  asyncio.run(main())
