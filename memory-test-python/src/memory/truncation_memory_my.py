from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage, trim_messages
from tiktoken import get_encoding


def message_count_truncation():
  history = InMemoryChatMessageHistory()
  max_messages = 4

  messages = [
      {"type": "human", "content": "我叫张三"},
      {"type": "ai", "content": "你好张三，很高兴认识你！"},
      {"type": "human", "content": "我今年25岁"},
      {"type": "ai", "content": "25岁正是青春年华，有什么我可以帮助你的吗？"},
      {"type": "human", "content": "我喜欢编程"},
      {"type": "ai", "content": "编程很有趣！你主要用什么语言？"},
      {"type": "human", "content": "我住在北京"},
      {"type": "ai", "content": "北京是个很棒的城市！"},
      {"type": "human", "content": "我的职业是软件工程师"},
      {"type": "ai", "content": "软件工程师是个很有前景的职业！"},
  ]

  for msg in messages:
    if msg["type"] == "human":
      history.add_message(HumanMessage(msg["content"]))
    else:
      history.add_message(AIMessage(msg["content"]))

  all_messages = history.messages
  trimmed_messages = all_messages[-max_messages:]

  print(f"保留消息数量: {len(trimmed_messages)}")
  print(
      "保留的消息:\n",
      "\n".join(
          f"{
              type(m).__name__}: {
              m.content}" for m in trimmed_messages))


def token_count_truncation():
  history = InMemoryChatMessageHistory()
  max_tokens = 70

  messages = [
      {"type": "human", "content": "我叫李四"},
      {"type": "ai", "content": "你好李四，很高兴认识你！"},
      {"type": "human", "content": "我是一名设计师"},
      {"type": "ai", "content": "设计师是个很有创造力的职业！你主要做什么类型的设计？"},
      {"type": "human", "content": "我喜欢艺术和音乐"},
      {"type": "ai", "content": "艺术和音乐都是很好的爱好，它们能激发创作灵感。"},
      {"type": "human", "content": "我擅长 UI/UX 设计"},
      {"type": "ai", "content": "UI/UX 设计非常重要，好的用户体验能让产品更成功！"},
  ]

  enc = get_encoding("cl100k_base")

  for msg in messages:
    if msg["type"] == "human":
      history.add_message(HumanMessage(msg["content"]))
    else:
      history.add_message(AIMessage(msg["content"]))

  all_messages = history.messages

  trimmed_messages = trim_messages(
      all_messages,
      max_tokens=max_tokens,
      token_counter=lambda msgs: sum(len(enc.encode(msg.content)) for msg in msgs),
      strategy="last",
  )

  total_tokens = sum(len(enc.encode(msg.content)) for msg in trimmed_messages)
  print(f"总 token 数: {total_tokens}/{max_tokens}")
  print(f"保留消息数量: {len(trimmed_messages)}")
  print(
      "保留的消息:\n", "\n".join(
          f"{
              type(m).__name__}: {
              m.content}" for m in trimmed_messages))


def run_all():
  message_count_truncation()
  token_count_truncation()


if __name__ == "__main__":
  run_all()
