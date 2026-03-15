# `client.session()` 详解

## 核心概念

`client.session()` 是一个**异步上下文管理器**（async context manager），它用于创建一个与特定 MCP 服务器的**持久连接会话**。

## 两种使用方式对比

### 方式 1: 使用 `client.session()` (推荐)

```python
async with client.session("my-mcp-server") as session:
    # 在这个会话内：
    # 1. 连接已建立并保持
    # 2. 可以多次调用 session 的方法
    # 3. 退出 with 块时自动关闭连接
    
    tools = await load_mcp_tools(session)
    resources = await session.list_resources()
    content = await session.read_resource(resource_uri)
    # ... 更多操作
```

**优点：**
- ✅ **连接复用**：一次建立连接，多次使用
- ✅ **资源管理**：自动管理连接生命周期（进入时建立，退出时关闭）
- ✅ **性能更好**：避免重复建立/关闭连接
- ✅ **支持资源操作**：可以直接调用 `session.list_resources()` 和 `session.read_resource()`

### 方式 2: 直接使用 `client.get_tools()` (简化版)

```python
# 每次调用都会创建新连接
tools = await client.get_tools()
resources = await client.get_resources()
```

**特点：**
- ⚠️ **每次调用都创建新连接**：`get_tools()` 内部会创建临时 session
- ⚠️ **性能开销**：多次调用会有连接建立/关闭的开销
- ✅ **使用简单**：不需要管理 session 生命周期

## `session()` 返回的对象

`client.session("server-name")` 返回的是 MCP 的 `ClientSession` 对象，它提供了以下方法：

```python
session.list_resources()      # 列出所有资源
session.read_resource(uri)    # 读取特定资源
session.call_tool(name, args) # 调用工具（通常通过 load_mcp_tools 更简单）
```

## 实际执行流程

```python
async with client.session("my-mcp-server") as session:
    # 1. 进入 with 块时：
    #    - 启动 MCP 服务器进程（如果使用 stdio transport）
    #    - 建立与服务器的连接
    #    - 初始化 MCP 协议握手
    
    # 2. 在 with 块内：
    tools = await load_mcp_tools(session)  # 通过 session 获取工具
    # ... 使用 session 进行各种操作
    
    # 3. 退出 with 块时：
    #    - 自动关闭连接
    #    - 清理资源
    #    - 终止服务器进程（如果适用）
```

## 为什么需要 session？

MCP (Model Context Protocol) 是一个**有状态的协议**：
- 需要建立连接
- 需要初始化握手
- 需要维护连接状态
- 需要正确关闭连接

`session()` 确保这些操作都正确执行，避免资源泄漏。

## 类比理解

可以把它想象成：

```python
# 类似数据库连接
async with db_pool.acquire() as conn:
    # 使用同一个连接执行多个操作
    result1 = await conn.execute(query1)
    result2 = await conn.execute(query2)
    # 退出时自动归还连接
```

## 最佳实践

**推荐使用 `session()` 的场景：**
- 需要访问资源（resources）
- 需要多次调用工具
- 需要更好的性能
- 需要精确控制连接生命周期

**可以使用 `get_tools()` 的场景：**
- 只需要工具列表，不需要资源
- 一次性使用，不需要复用连接
- 代码更简洁的场景
