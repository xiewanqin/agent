import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage, get_buffer_string
from tiktoken import get_encoding

load_dotenv()

enc = get_encoding("cl100k_base")

model = init_chat_model(
    f"openai:{os.getenv('MODEL_NAME')}",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)


def count_tokens(messages, encoder):
  total = 0
  for msg in messages:
    content = msg.content if isinstance(msg.content, str) else str(msg.content)
    total += len(encoder.encode(content))
  return total


def summarization_memory_demo():
  history = InMemoryChatMessageHistory()
  max_tokens = 200  # 超过此 token 数触发总结（与 JS 版一致）
  keep_recent_tokens = 80  # 保留最近消息的 token 上限

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
  total_tokens = count_tokens(all_messages, enc)

  print(f"当前对话总 token 数: {total_tokens}（阈值: {max_tokens}）")

  if total_tokens >= max_tokens:
    # 从后往前累加，保留「最近」的消息直到达到 keep_recent_tokens（与 JS 一致）
    recent_messages = []
    recent_token_sum = 0
    for msg in reversed(all_messages):
      content = msg.content if isinstance(msg.content, str) else str(msg.content)
      msg_tokens = len(enc.encode(content))
      if recent_token_sum + msg_tokens <= keep_recent_tokens:
        recent_messages.insert(0, msg)
        recent_token_sum += msg_tokens
      else:
        break

    n_keep = len(recent_messages)
    messages_to_summarize = all_messages[: len(all_messages) - n_keep]
    summarize_tokens = count_tokens(messages_to_summarize, enc)

    print("\n💡 Token 数量超过阈值，开始总结...")
    print(f"📝 将被总结的消息数量: {len(messages_to_summarize)} ({summarize_tokens} tokens)")
    print(f"📝 将被保留的消息数量: {len(recent_messages)} ({recent_token_sum} tokens)")

    summary = summarize_history(messages_to_summarize)

    history.clear()
    for msg in recent_messages:
      history.add_message(msg)

    print(f"\n保留消息数量: {len(recent_messages)}")
    lines = []
    for m in recent_messages:
      c = m.content if isinstance(m.content, str) else str(m.content)
      t = len(enc.encode(c))
      lines.append(f"{type(m).__name__} ({t} tokens): {m.content}")
    print("保留的消息:", "\n  ".join(lines))
    print(f"\n总结内容（不包含保留的消息）: {summary}")
  else:
    print(f"\nToken 数量 ({total_tokens}) 未超过阈值 ({max_tokens})，无需总结")


def summarize_history(messages):
  if len(messages) == 0:
    return ""
  conversation_text = get_buffer_string(
      messages,
      human_prefix="用户",
      ai_prefix="助手",
  )
  summary_prompt = f"请总结以下对话的核心内容，保留重要信息：\n\n{conversation_text}\n\n总结："
  summary_response = model.invoke([HumanMessage(content=summary_prompt)])
  return summary_response.content


if __name__ == "__main__":
  summarization_memory_demo()
