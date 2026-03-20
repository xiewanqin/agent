import os
from dotenv import load_dotenv
from pymilvus import MilvusClient
from langchain_community.embeddings import DashScopeEmbeddings

load_dotenv()

COLLECTION_NAME = 'ai_diary4'
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


def update_diary(id: str, content: str, date: str, mood: str, tags: list[str]):
  vector = get_embedding(content)
  data = {
      "id": id,
      "content": content,
      "date": date,
      "mood": mood,
      "tags": tags,
      "vector": vector
  }
  client.upsert(collection_name=COLLECTION_NAME, data=[data])


def main():
  try:
    print('Connecting to Milvus...')
    print('✓ Connected\n')

    print('Updating diary entry...')
    updated_content = {
        'id': 'diary_001',
        'content': '今天下了一整天的雨，心情很糟糕。工作上遇到了很多困难，感觉压力很大。一个人在家，感觉特别孤独。',
        'date': '2026-01-10',
        'mood': 'happy',
        'tags': ['生活', '散步']
    }
    update_diary(**updated_content)
    print('✓ Updated diary entry: diary_001\n')
    print(f'  New content: {updated_content["content"]}')
    print(f'  New mood: {updated_content["mood"]}')
    print(f'  New tags: {", ".join(updated_content["tags"])}')
  except Exception as e:
    print(f'Error: {e}')


if __name__ == '__main__':
  main()
