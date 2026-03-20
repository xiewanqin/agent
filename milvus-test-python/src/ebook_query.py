import os
from dotenv import load_dotenv
from pymilvus import MilvusClient
from langchain_community.embeddings import DashScopeEmbeddings

load_dotenv()

COLLECTION_NAME = 'ebook_collection1'
VECTOR_DIM = 1024

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


def main():
  try:
    print('Loading collection...')
    client.load_collection(collection_name=COLLECTION_NAME)
    print('✓ Collection loaded')

    print('Searching for similar ebook content...')
    query = '鸠摩智会什么武功？'
    print(f'Query: "{query}"\n')
    query_vector = get_embedding(query)
    search_result = client.search(
        collection_name=COLLECTION_NAME,
        data=[query_vector],
        anns_field='vector',
        limit=5,
        search_params={'metric_type': 'COSINE'},
        output_fields=['id', 'book_id', 'chapter_num', 'index', 'content']
    )
    print(f'Found {len(search_result[0])} results:\n')
    for results in search_result:
      for index, result in enumerate(results):
        print(f'{index + 1}. [Score: {result["distance"]:.4f}]')
        print(f'   ID: {result["id"]}')
        print(f'   Book ID: {result["book_id"]}')
        print(f'   Chapter: 第 {result["chapter_num"]} 章')
        print(f'   Index: {result["index"]}')
        print(f'   Content: {result["content"]}\n')
  except Exception as e:
    print(f'Error: {e}')


if __name__ == '__main__':
  main()
