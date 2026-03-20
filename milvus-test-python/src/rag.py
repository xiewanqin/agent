import os
from dotenv import load_dotenv
from pymilvus import MilvusClient
# from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import DashScopeEmbeddings
# from langchain_core.agents import create_agent

load_dotenv()

COLLECTION_NAME = 'ai_diary4'
VECTOR_DIM = 1024

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    temperature=0.7,
)

embeddings = DashScopeEmbeddings(
    dashscope_api_key=os.getenv("OPENAI_API_KEY"),
    model=os.getenv("EMBEDDINGS_MODEL_NAME", "text-embedding-v3"),
)

milvus_uri = os.getenv("MILVUS_ADDRESS", "localhost:19530")
if not milvus_uri.startswith("http"):
  milvus_uri = f"http://{milvus_uri}"


client = MilvusClient(uri=milvus_uri)


def get_embedding(text: str) -> list[float]:
  return embeddings.embed_query(text)


def retrieve_relevant_diaries(question: str, k: int = 2) -> list[dict]:
  query_vector = get_embedding(question)
  search_result = client.search(
      collection_name=COLLECTION_NAME,
      data=[query_vector],
      anns_field='vector',
      limit=k,
      search_params={'metric_type': 'COSINE'},
      output_fields=['id', 'content', 'date', 'mood', 'tags']
  )
  return search_result[0]


def answer_diary_question(question: str, k: int = 2) -> str:
  print('=' * 80)
  print(f"问题: {question}")
  print('=' * 80)

  retrieved_diaries = retrieve_relevant_diaries(question, k)
  if not retrieved_diaries:
    return '抱歉，我没有找到相关的日记内容。'

  context = "\n\n━━━━━\n\n".join(
      f"[日记 {
          i +
          1}] 相似度: {
          result['distance']:.4f}\n日期: {
          result['date']}\n心情: {
          result['mood']}\n标签: {
          result['tags']}\n内容: {
              result['content']}" for i,
      result in enumerate(retrieved_diaries))
  print(context)
  print('=' * 80)
  prompt = f"""你是一个温暖贴心的 AI 日记助手。基于用户的日记内容回答问题，用亲切自然的语言。

请根据以下日记内容回答问题：
{context}

用户问题: {question}

回答要求：
1. 如果日记中有相关信息，请结合日记内容给出详细、温暖的回答
2. 可以总结多篇日记的内容，找出共同点或趋势
3. 如果日记中没有相关信息，请温和地告知用户
4. 用第一人称"你"来称呼日记的作者
5. 回答要有同理心，让用户感到被理解和关心

AI 助手的回答:
"""

  response = model.invoke(prompt)
  print(f"AI 助手的回答: {response.content}")
  print('\n')
  return response.content


if __name__ == '__main__':
  answer_diary_question('我今天很开心')
