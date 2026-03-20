import os
from pickle import HIGHEST_PROTOCOL
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.messages import HumanMessage, SystemMessage
from pathlib import Path

load_dotenv()

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)


def file_history_demo():
  filePath = Path.cwd() / "chat_history.json"

  systemMessage = SystemMessage(content="你是一个友好、幽默的做菜助手，喜欢分享美食和烹饪技巧。")
  history = FileChatMessageHistory(file_path=str(filePath))

  user_message1 = HumanMessage(content="你今天吃的什么？")
  history.add_message(user_message1)
  messages1 = [systemMessage] + history.messages
  response1 = model.invoke(messages1)
  history.add_message(response1)
  print(f"用户: {user_message1.content}")
  print(f"助手: {response1.content}\n")

  user_message2 = HumanMessage(content="好吃吗？")
  history.add_message(user_message2)
  messages2 = [systemMessage] + history.messages
  response2 = model.invoke(messages2)
  history.add_message(response2)
  print(f"用户: {user_message2.content}")
  print(f"助手: {response2.content}\n")

  all_messages = history.messages
  print(f"共保存了 {len(all_messages)} 条消息：")
  for index, msg in enumerate(all_messages):
    prefix = "用户" if msg.type == "human" else "助手"
    content = str(msg.content)[:50]
    print(f"  {index + 1}. [{prefix}]: {content}...")


if __name__ == "__main__":
  file_history_demo()
