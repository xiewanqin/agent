import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage, get_buffer_string

load_dotenv()

model = init_chat_model(
    f"openai:{os.getenv('MODEL_NAME')}",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)


def summarization_memory_demo():
  history = InMemoryChatMessageHistory()
  max_messages = 6  # 超过 6 条消息时触发总结

  messages = [
      {"type": "human", "content": "我想学做红烧肉，你能教我吗？"},
      {"type": "ai", "content": "当然可以！红烧肉是一道经典的中式菜肴。首先需要准备五花肉、冰糖、生抽、老抽、料酒等材料。"},
      {"type": "human", "content": "五花肉需要切多大块？"},
      {"type": "ai", "content": "建议切成3-4厘米见方的块，这样既容易入味，口感也更好。切好后可以用开水焯一下去除血沫。"},
      {"type": "human", "content": "炒糖色的时候有什么技巧吗？"},
      {"type": "ai", "content": "炒糖色是关键步骤。用小火慢慢炒，等冰糖完全融化变成焦糖色，冒小泡时就可以下肉了。注意不要炒过头，否则会发苦。"},
      {"type": "human", "content": "需要炖多长时间？"},
      {"type": "ai", "content": "一般需要炖40-60分钟，用小火慢炖，直到肉变得软糯入味。可以用筷子戳一下，能轻松戳透就说明好了。"},
      {"type": "human", "content": "最后收汁的时候要注意什么？"},
      {"type": "ai", "content": "收汁时要用大火，不断翻动，让汤汁均匀包裹在肉块上。看到汤汁变得浓稠，颜色红亮就可以出锅了。"},
  ]

  for msg in messages:
    if msg["type"] == "human":
      history.add_message(HumanMessage(msg["content"]))
    else:
      history.add_message(AIMessage(msg["content"]))

  all_messages = history.messages

  print(f"原始消息数量: {len(all_messages)}")
  print("原始消息:", "\n".join(f"{type(m).__name__}: {m.content}" for m in all_messages))

  if len(all_messages) >= max_messages:
    keep_recent = 2
    recent_messages = all_messages[-keep_recent:]
    messages_to_summarize = all_messages[:-keep_recent]

    print("\n💡 历史消息过多，开始总结...")
    print(f"📝 将被总结的消息数量: {len(messages_to_summarize)}")
    print(f"📝 将被保留的消息数量: {len(recent_messages)}")

    summary = summarize_history(messages_to_summarize)

    history.clear()
    for msg in recent_messages:
      history.add_message(msg)

    print(f"\n保留消息数量: {len(recent_messages)}")
    print(
        "保留的消息:", "\n".join(
            f"{
                type(m).__name__}: {
                m.content}" for m in recent_messages))
    print(f"\n总结内容（不包含保留的消息）: {summary}")


def summarize_history(messages):
  if len(messages) == 0:
    return ""

  conversation_text = get_buffer_string(
      messages,
      human_prefix="用户",
      ai_prefix="助手",
  )
  summary_prompt = f"请总结以下对话的核心内容，保留重要信息：\n\n{conversation_text}\n\n总结："

  # 阿里云 DashScope 等 API 要求至少包含 user 角色，用 HumanMessage 而非 SystemMessage
  summary_response = model.invoke([HumanMessage(content=summary_prompt)])
  return summary_response.content


if __name__ == "__main__":
  summarization_memory_demo()
