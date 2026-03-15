import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

# 加载API密钥
load_dotenv()

# 初始化大模型（以OpenAI为例，你也可以换成DeepSeek等）
llm = ChatOpenAI(
    temperature=0.7,
    model_name=os.getenv('MODEL_NAME', 'qwen-coder-turbo'),
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url=os.getenv('OPENAI_BASE_URL'),
)

# 使用消息列表来管理对话历史（相当于记忆功能）
messages = []

# 开始对话
print("Agent已启动，输入'退出'结束对话")
while True:
    user_input = input("\n你: ")
    if user_input.lower() in ['退出', 'exit', 'quit']:
        break
    
    # 添加用户消息到历史
    messages.append(HumanMessage(content=user_input))
    
    # 调用模型
    response = llm.invoke(messages)
    # 添加AI回复到历史
    messages.append(AIMessage(content=response.content))
    
    print(f"Agent: {response.content}")