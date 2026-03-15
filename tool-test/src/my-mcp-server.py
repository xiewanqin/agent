from mcp.server.fastmcp import FastMCP

# 数据库
DATABASE = {
    "users": {
        "001": {"id": "001", "name": "张三", "email": "zhangsan@example.com", "role": "admin"},
        "002": {"id": "002", "name": "李四", "email": "lisi@example.com", "role": "user"},
        "003": {"id": "003", "name": "王五", "email": "wangwu@example.com", "role": "user"},
    }
}

mcp = FastMCP("my-mcp-server")


@mcp.tool()
def query_user(user_id: str) -> str:
    """查询数据库中的用户信息。输入用户 ID，返回该用户的详细信息（姓名、邮箱、角色）。

    Args:
        user_id: 用户 ID，例如: 001, 002, 003
    """
    user = DATABASE["users"].get(user_id)
    if not user:
        return f"用户 ID {user_id} 不存在。可用的 ID: 001, 002, 003"

    return (
        f"用户信息：\n"
        f"- ID: {user['id']}\n"
        f"- 姓名: {user['name']}\n"
        f"- 邮箱: {user['email']}\n"
        f"- 角色: {user['role']}"
    )


@mcp.resource("docs://guide")
def usage_guide() -> str:
    """MCP Server 使用文档"""
    return (
        "MCP Server 使用指南\n\n"
        "功能：提供用户查询等工具。\n\n"
        "使用：在 Cursor 等 MCP Client 中通过自然语言对话，Cursor 会自动调用相应工具。"
    )


if __name__ == "__main__":
    mcp.run()
