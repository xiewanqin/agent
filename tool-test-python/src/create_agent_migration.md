# 使用 create_agent 重构说明

## 主要改动

### 之前：手动工具调用循环

```python
# 需要手动编写循环逻辑
for _ in range(max_iterations):
    response = await model_with_tools.ainvoke(messages)
    messages.append(response)
    
    if not response.tool_calls:
        return response.content
    
    # 手动执行每个工具调用
    for tool_call in response.tool_calls:
        tool_result = await found_tool.invoke(tool_call["args"])
        messages.append(ToolMessage(...))
```

**问题：**
- ❌ 代码冗长，需要手动管理消息历史
- ❌ 需要手动判断何时停止
- ❌ 错误处理复杂
- ❌ 难以调试

### 现在：使用 create_agent

```python
# 一行代码创建 agent，自动处理所有逻辑
graph = create_agent(
    model=model,
    tools=tools,
    system_prompt=resource_content,
)

# 直接调用，自动处理工具调用循环
result = await graph.ainvoke({
    "messages": [{"role": "user", "content": query}]
})
```

**优势：**
- ✅ 代码简洁，只需几行
- ✅ 自动处理工具调用循环
- ✅ 自动管理消息历史
- ✅ 自动判断何时停止
- ✅ 内置错误处理
- ✅ 支持流式输出

## create_agent 的核心特性

### 1. 自动工具调用循环

`create_agent` 内部会自动：
- 调用模型获取响应
- 检查是否有工具调用
- 执行工具调用
- 将工具结果添加到消息历史
- 再次调用模型
- 重复直到不再调用工具

### 2. 消息历史管理

自动管理完整的对话历史：
- `HumanMessage` - 用户输入
- `AIMessage` with `tool_calls` - AI 决定调用工具
- `ToolMessage` - 工具执行结果
- `AIMessage` without `tool_calls` - AI 最终回复

### 3. 流式输出支持

可以实时查看 agent 执行过程：

```python
async for chunk in graph.astream(inputs, stream_mode="updates"):
    for node_name, node_output in chunk.items():
        if node_name == "agent":
            print("Agent 正在思考...")
        elif node_name == "tools":
            print("正在执行工具...")
```

### 4. 系统提示词支持

可以直接传入 `system_prompt`，agent 会自动使用：

```python
graph = create_agent(
    model=model,
    tools=tools,
    system_prompt="你是一个有用的助手...",
)
```

## 代码对比

### 之前（手动循环）：~70 行

```python
async def run_agent_with_tools(query: str, max_iterations: int = 30) -> str:
    messages = [SystemMessage(...), HumanMessage(...)]
    
    for _ in range(max_iterations):
        response = await model_with_tools.ainvoke(messages)
        messages.append(response)
        
        if not response.tool_calls:
            return response.content
        
        for tool_call in response.tool_calls:
            found_tool = next(...)
            if found_tool:
                tool_result = await found_tool.invoke(...)
                messages.append(ToolMessage(...))
    
    return messages[-1].content
```

### 现在（create_agent）：~10 行

```python
graph = create_agent(model=model, tools=tools, system_prompt=...)

async def run_agent(query: str):
    result = await graph.ainvoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].content
```

## 使用建议

1. **默认使用 `ainvoke()`** - 直接获取最终结果，性能最好
2. **调试时使用 `astream()`** - 可以看到执行过程
3. **使用 `system_prompt`** - 可以传入资源内容或指令
4. **保持 `session()` 管理连接** - 确保连接复用和资源管理

## 迁移指南

如果你有其他使用手动循环的代码，可以这样迁移：

1. 导入 `create_agent`：
   ```python
   from langchain.agents import create_agent
   ```

2. 创建 agent：
   ```python
   graph = create_agent(model=model, tools=tools)
   ```

3. 替换循环逻辑：
   ```python
   # 之前
   result = await run_agent_with_tools(query)
   
   # 现在
   result = await graph.ainvoke({"messages": [{"role": "user", "content": query}]})
   ```

4. 提取结果：
   ```python
   final_reply = result["messages"][-1].content
   ```

## 总结

使用 `create_agent` 是 LangChain 1.0 的推荐方式，它：
- 简化了代码
- 提高了可维护性
- 提供了更好的错误处理
- 支持流式输出
- 自动管理复杂的状态

**建议：所有新项目都应该使用 `create_agent` 而不是手动编写工具调用循环。**
