import os
from dotenv import load_dotenv
from pymilvus import MilvusClient
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_openai import ChatOpenAI

load_dotenv()

COLLECTION_NAME = 'ebook_collection1'
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


def retrieve_relevant_ebook_content(question: str, k: int = 5) -> list[dict]:
  query_vector = get_embedding(question)
  search_result = client.search(
      collection_name=COLLECTION_NAME,
      data=[query_vector],
      anns_field='vector',
      limit=k,
      search_params={'metric_type': 'COSINE'},
      output_fields=['id', 'book_id', 'chapter_num', 'index', 'content']
  )
  return search_result[0]


def answer_ebook_question(question: str, k: int = 5) -> str:
  print('=' * 80)
  print(f'问题: {question}')
  print('=' * 80)

  print('\n【检索相关内容】')
  retrieved_content = retrieve_relevant_ebook_content(question, k)
  if not retrieved_content:
    print('未找到相关内容')
    return '抱歉，我没有找到相关的《天龙八部》内容。'

  print(f'Found {len(retrieved_content)} results:\n')
  for index, result in enumerate(retrieved_content):
    print(f'{index + 1}. [相似度: {result["distance"]:.4f}]')
    print(f'   ID: {result["id"]}')
    print(f'   Book ID: {result["book_id"]}')
    print(f'   Chapter: 第 {result["chapter_num"]} 章')
    print(f'   Index: {result["index"]}')
    print(f'   Content: {result["content"]}\n')

  context = "\n\n━━━━━\n\n".join(
      f"[片段 {i + 1}] 章节: 第 {result['chapter_num']} 章内容: {result['content']}" for i,
      result in enumerate(retrieved_content))

  print('=' * 80)

  prompt = f"""你是一个专业的《天龙八部》小说助手。基于小说内容回答问题，用准确、详细的语言。

请根据以下《天龙八部》小说片段内容回答问题：
{context}

用户问题: {question}

回答要求：
1. 如果片段中有相关信息，请结合小说内容给出详细、准确的回答
2. 可以综合多个片段的内容，提供完整的答案
3. 如果片段中没有相关信息，请如实告知用户
4. 回答要准确，符合小说的情节和人物设定
5. 可以引用原文内容来支持你的回答

AI 助手的回答:
"""

  response = model.invoke(prompt)
  print(f'AI 助手的回答: {response.content}')
  print('\n')


def main():
  try:
    print('Loading collection...')
    client.load_collection(collection_name=COLLECTION_NAME)
    print('✓ Collection loaded')

    query = '鸠摩智会什么武功？'

    answer_ebook_question(query, 5)

    print('=' * 80)
    print('处理完成！')
    print('=' * 80)

  except Exception as e:
    print(f'Error: {e}')


if __name__ == '__main__':
  main()
