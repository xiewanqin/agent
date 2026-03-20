import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)


async def in_memory_demo():
    history = InMemoryChatMessageHistory()

    system_message = SystemMessage(
        content="你是一个友好、幽默的做菜助手，喜欢分享美食和烹饪技巧。"
    )

    # 第一轮对话
    print("[第一轮对话]")
    user_message_1 = HumanMessage(content="你今天吃的什么？")
    history.add_message(user_message_1)

    messages_1 = [system_message] + history.messages
    response_1 = await model.ainvoke(messages_1)
    history.add_message(response_1)

    print(f"用户: {user_message_1.content}")
    print(f"助手: {response_1.content}\n")

    # 第二轮对话（基于历史记录）
    print("[第二轮对话 - 基于历史记录]")
    user_message_2 = HumanMessage(content="好吃吗？")
    history.add_message(user_message_2)

    messages_2 = [system_message] + history.messages
    response_2 = await model.ainvoke(messages_2)
    history.add_message(response_2)

    print(f"用户: {user_message_2.content}")
    print(f"助手: {response_2.content}\n")

    # 展示所有历史消息
    print("[历史消息记录]")
    all_messages = history.messages
    print(f"共保存了 {len(all_messages)} 条消息：")
    for index, msg in enumerate(all_messages):
        prefix = "用户" if msg.type == "human" else "助手"
        content = str(msg.content)[:50]
        print(f"  {index + 1}. [{prefix}]: {content}...")


if __name__ == "__main__":
    import asyncio

    asyncio.run(in_memory_demo())
