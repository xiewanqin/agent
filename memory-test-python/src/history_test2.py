import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv()

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)


def file_history_demo():
    # 指定存储文件的路径
    file_path = Path.cwd() / "chat_history.json"

    # 系统提示词
    system_message = SystemMessage(
        content="你是一个友好的做菜助手，喜欢分享美食和烹饪技巧。"
    )

    print("[第一轮对话]")
    history = FileChatMessageHistory(file_path=str(file_path))

    user_message_1 = HumanMessage(content="红烧肉怎么做")
    history.add_message(user_message_1)

    messages_1 = [system_message] + history.messages
    response_1 = model.invoke(messages_1)
    history.add_message(response_1)

    print(f"用户: {user_message_1.content}")
    print(f"助手: {response_1.content}")
    print(f"✓ 对话已保存到文件: {file_path}\n")

    print("[第二轮对话]")
    user_message_2 = HumanMessage(content="好吃吗？")
    history.add_message(user_message_2)

    messages_2 = [system_message] + history.messages
    response_2 = model.invoke(messages_2)
    history.add_message(response_2)

    print(f"用户: {user_message_2.content}")
    print(f"助手: {response_2.content}")
    print("✓ 对话已更新到文件\n")


if __name__ == "__main__":
    file_history_demo()
