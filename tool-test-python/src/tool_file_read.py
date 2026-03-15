"""
Python 版本的 LangChain 工具调用示例
对应 JavaScript 版本的 tool-file-read.mjs
"""
import os
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from pydantic import BaseModel, Field

# ==================== 加载环境变量 ====================
load_dotenv()

# ==================== 第一步：创建 AI 模型 ====================
# 创建一个聊天模型，配置 API 密钥和基础 URL
model = ChatOpenAI(
    model_name=os.getenv("MODEL_NAME", "qwen-coder-turbo"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)

# ==================== 第二步：定义工具 ====================
# 创建一个"读取文件"的工具
# 这个工具可以被 AI 模型调用来读取文件内容

# 定义工具的参数结构（使用 Pydantic）
class ReadFileInput(BaseModel):
    """读取文件的输入参数"""
    file_path: str = Field(description="要读取的文件路径")

@tool(args_schema=ReadFileInput)
def read_file(file_path: str) -> str:
    """
    用此工具来读取文件内容。
    当用户要求读取文件、查看代码、分析文件内容时，调用此工具。
    输入文件路径（可以是相对路径或绝对路径）。
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"  [工具调用] read_file(\"{file_path}\") - 成功读取 {len(content)} 字节")
        return f"文件内容:\n{content}"
    except Exception as e:
        return f"错误: {str(e)}"

# 将所有工具放在一个列表中
tools = [read_file]

# ==================== 第三步：给模型绑定工具 ====================
# 这一步很关键！绑定后，AI 模型就知道可以使用哪些工具了
model_with_tools = model.bind_tools(tools)

# ==================== 第四步：准备对话消息 ====================
messages = [
    # 系统消息：告诉 AI 它的角色和工作方式（必须放在最前面！）
    SystemMessage(content="""你是一个代码助手，可以使用工具读取文件并解释代码。

工作流程：
1. 用户要求读取文件时，立即调用 read_file 工具
2. 等待工具返回文件内容
3. 基于文件内容进行分析和解释

可用工具：
- read_file: 读取文件内容（使用此工具来获取文件内容）
"""),
    # 用户消息：用户的请求（放在系统消息之后）
    HumanMessage(content="请读取 ./src/tool_file_read.py 文件内容并解释代码")
]

# ==================== 第五步：开始对话循环 ====================
async def main():
    print('[步骤1] 第一次调用 AI 模型...')
    response = await model_with_tools.ainvoke(messages)
    print('[步骤1完成] AI 返回了响应')
    
    print(f"[响应类型] tool_calls: {len(response.tool_calls) if response.tool_calls else 0}, content: {'有内容' if response.content else '无内容'}")

    # 将 AI 的响应保存到消息历史中
    messages.append(response)

    # ==================== 第六步：处理工具调用循环 ====================
    # 如果 AI 返回了工具调用请求，我们需要执行工具，然后把结果返回给 AI
    max_iterations = 10  # 防止无限循环
    iteration_count = 0

    # 只要 AI 还在请求调用工具，就继续循环
    while response.tool_calls and iteration_count < max_iterations:
        iteration_count += 1
        
        print(f"\n[步骤2-{iteration_count}] 检测到 {len(response.tool_calls)} 个工具调用")
        
        # ========== 2.1 执行所有工具调用 ==========
        # AI 可能同时请求调用多个工具，先收集所有结果（便于后续改为并行执行）
        tool_results = []
        for tool_call in response.tool_calls:
            # 根据工具名称找到对应的工具函数
            tool = next((t for t in tools if t.name == tool_call["name"]), None)
            if not tool:
                tool_results.append(f"错误: 找不到工具 {tool_call['name']}")
                continue
            
            print(f"  [执行工具] {tool_call['name']}({tool_call.get('args', {})})")
            try:
                # 执行工具，传入 AI 提供的参数
                # Python 中工具调用需要手动处理参数
                args = tool_call.get("args", {})
                result = tool.invoke(args)
                tool_results.append(result)
            except Exception as error:
                tool_results.append(f"错误: {str(error)}")
        
        # ========== 2.2 将工具执行结果告诉 AI ==========
        # 工具执行完后，需要把结果以 ToolMessage 的形式返回给 AI
        for tool_call, result in zip(response.tool_calls, tool_results):
            messages.append(
                ToolMessage(
                    content=result,  # 工具的执行结果
                    tool_call_id=tool_call.get("id"),  # 关联到对应的工具调用
                )
            )
        
        # ========== 2.3 再次调用 AI，让它基于工具结果生成回复 ==========
        print(f"[步骤3-{iteration_count}] 将工具结果发送给 AI，等待最终回复...")
        response = await model_with_tools.ainvoke(messages)
        messages.append(response)
        
        # 检查 AI 是否还需要调用更多工具
        if response.tool_calls:
            print(f"[步骤3-{iteration_count}完成] AI 又返回了 {len(response.tool_calls)} 个工具调用，继续循环...")
        else:
            print(f"[步骤3-{iteration_count}完成] AI 返回了最终回复，退出循环")

    # ==================== 第七步：输出最终结果 ====================
    if iteration_count >= max_iterations and response.tool_calls:
        print(f"\n⚠️ 警告: 达到最大迭代次数 ({max_iterations})，强制退出循环")

    print('\n========== 最终回复 ==========')
    print(response.content)

# 运行主函数
if __name__ == "__main__":
    asyncio.run(main())
