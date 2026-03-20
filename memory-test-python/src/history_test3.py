import os
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
  restoredMessages = history.messages
  print(f"从文件恢复了 {len(restoredMessages)} 条历史消息：")

  for index, msg in enumerate(restoredMessages):
    prefix = "用户" if msg.type == "human" else "助手"
    content = str(msg.content)[:50]
    print(f"  {index + 1}. [{prefix}]: {content}...")

  print("[第三轮对话]")
  userMessage3 = HumanMessage(content="需要哪些食材？")
  history.add_message(userMessage3)
  messages3 = [systemMessage] + history.messages
  response3 = model.invoke(messages3)
  history.add_message(response3)
  print(f"用户: {userMessage3.content}")
  print(f"助手: {response3.content}\n")


if __name__ == "__main__":
  file_history_demo()
