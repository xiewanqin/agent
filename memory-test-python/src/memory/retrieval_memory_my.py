import os
from datetime import datetime

from dotenv import load_dotenv
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from pymilvus import MilvusClient

COLLECTION_NAME = "conversations"

load_dotenv()

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)

embeddings = DashScopeEmbeddings(
    dashscope_api_key=os.getenv("OPENAI_API_KEY"),
    model=os.getenv("EMBEDDINGS_MODEL_NAME"),
)

milvus_uri = os.getenv("MILVUS_ADDRESS", "localhost:19530")
if not milvus_uri.startswith("http"):
  milvus_uri = f"http://{milvus_uri}"

client = MilvusClient(uri=milvus_uri)


def get_embedding(text: str) -> list[float]:
  return embeddings.embed_query(text)


def retrieve_relevant_conversations(query: str, k: int = 2) -> list[dict]:
  """Milvus Python SDK 返回的每条命中含 distance（COSINE 下可作相似度参考）。"""
  try:
    query_vector = get_embedding(query)
    search_result = client.search(
        collection_name=COLLECTION_NAME,
        data=[query_vector],
        anns_field="vector",
        limit=k,
        search_params={"metric_type": "COSINE"},
        output_fields=["id", "content", "round", "timestamp"],
    )
    return search_result[0] if search_result else []
  except Exception as e:
    print(f"检索对话时出错: {e}")
    return []


def retrieval_memory_demo():
  history = InMemoryChatMessageHistory()
  # 字典的键必须是字符串，不能写 {input: ...}（那是非法 Python）
  conversations = [
      {"input": "我之前提到的机器学习项目进展如何？"},
      {"input": "我周末经常做什么？"},
      {"input": "我的职业是什么？"},
  ]

  # 正确写法：enumerate 得到下标和整条 dict，再取 ["input"]
  for i, conv in enumerate(conversations):
    user_text = conv["input"]
    user_message = HumanMessage(content=user_text)

    print(f"\n[第 {i + 1} 轮对话]")
    print(f"用户: {user_text}")
    print("\n【检索相关历史对话】")

    retrieved = retrieve_relevant_conversations(user_text, 2)

    relevant_history = ""
    if retrieved:
      for idx, hit in enumerate(retrieved):
        # pymilvus 用 distance，不是 score
        dist = float(hit.get("distance", 0))
        print(f"\n[历史对话 {idx + 1}] 距离/相似度相关值: {dist:.4f}")
        print(f"轮次: {hit['round']}")
        print(f"内容: {hit['content']}")
      relevant_history = "\n\n━━━━━\n\n".join(
          f"【历史对话 {idx + 1}】\n轮次: {hit['round']}\n{hit['content']}"
          for idx, hit in enumerate(retrieved)
      )
    else:
      print("未找到相关历史对话")

    context_messages = (
        [
            HumanMessage(
                content=f"相关历史对话：\n{relevant_history}\n\n用户问题: {user_text}"
            )
        ]
        if relevant_history
        else [user_message]
    )

    print("\n【AI 回答】")
    response = model.invoke(context_messages)
    history.add_message(user_message)
    history.add_message(response)
    print(f"助手: {response.content}\n")
    print(f"共保存了 {len(history.messages)} 条消息")

    conversation_text = f"用户: {user_text}\n助手: {response.content}"
    # Python f-string 用花括号，不要写成 JS 的 $ 或 ${}
    conv_id = f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i + 1}"
    conversation_vector = get_embedding(conversation_text)

    try:
      client.insert(
          collection_name=COLLECTION_NAME,
          data=[
              {
                  "id": conv_id,
                  "vector": conversation_vector,
                  "content": conversation_text,
                  "round": i + 1,
                  "timestamp": datetime.now().isoformat(),
              }
          ],
      )
      print(f"已保存到 Milvus 向量数据库: {conv_id}")
    except Exception as e:
      print(f"保存到向量数据库时出错: {e}")


if __name__ == "__main__":
  retrieval_memory_demo()
