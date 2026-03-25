import os
from dotenv import load_dotenv
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.3,
    base_url=os.getenv("OPENAI_BASE_URL"),
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个简洁、有帮助的中文助手，会用 1-2 句话回答用户问题，重点给出明确、有用的信息。"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])

simple_chain = prompt | model | StrOutputParser()

message_histories = {}


def get_message_history(session_id):
  if session_id not in message_histories:
    message_histories[session_id] = InMemoryChatMessageHistory()
  return message_histories[session_id]


chain = RunnableWithMessageHistory(
    runnable=simple_chain,
    get_session_history=get_message_history,
    input_messages_key="question",
    history_messages_key="history",
)

# 第一次对话
print("--- 第一次对话（提供信息） ---")
result1 = chain.invoke(
    {"question": "我的名字是神光，我来自山东，我喜欢编程、写作、金铲铲。"},
    {"configurable": {"session_id": "user-123"}}
)
print(result1)

# 第二次对话
print("--- 第二次对话（基于历史记录） ---")
result2 = chain.invoke(
    {"question": "我刚才说我来自哪里？"},
    {"configurable": {"session_id": "user-123"}}
)
print(result2)

# 第三次对话
print("--- 第三次对话（询问之前的信息） ---")
result3 = chain.invoke(
    {"question": "我平时喜欢做什么？"},
    {"configurable": {"session_id": "user-123"}}
)
print(result3)
