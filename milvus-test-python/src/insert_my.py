import os
from dotenv import load_dotenv
from pymilvus import MilvusClient, CollectionSchema, FieldSchema, DataType
from langchain_community.embeddings import DashScopeEmbeddings

load_dotenv()

COLLECTION_NAME = 'ai_diary'
VECTOR_DIM = 1024

# DashScope 原生接口，比 OpenAI 兼容模式更稳定
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
    print("Connecting to Milvus...")
    print("✓ Connected\n")

    # 若集合已存在则先删除（便于重复运行）
    if client.has_collection(COLLECTION_NAME):
      print(f"Dropping existing collection '{COLLECTION_NAME}'...")
      client.drop_collection(COLLECTION_NAME)

    # 创建集合
    print("Creating collection...")
    schema = CollectionSchema(
        fields=[
            FieldSchema(
                name='id', dtype=DataType.VARCHAR, max_length=50, is_primary=True), FieldSchema(
                name='vector', dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIM), FieldSchema(
                name='content', dtype=DataType.VARCHAR, max_length=5000), FieldSchema(
                name='date', dtype=DataType.VARCHAR, max_length=50), FieldSchema(
                name='mood', dtype=DataType.VARCHAR, max_length=50), FieldSchema(
                name='tags', dtype=DataType.ARRAY, element_type=DataType.VARCHAR, max_capacity=10, max_length=50)])
    client.create_collection(
        collection_name=COLLECTION_NAME,
        schema=schema,
    )
    print("Collection created")

    # 创建索引
    print("\nCreating index...")
    index_params = client.prepare_index_params()
    index_params.add_index(
        field_name="vector",
        index_type="IVF_FLAT",
        metric_type="COSINE",
        params={"nlist": 1024},
    )
    client.create_index(
        collection_name=COLLECTION_NAME,
        index_params=index_params,
    )
    print("Index created")

    # 加载集合
    print("\nLoading collection...")
    client.load_collection(collection_name=COLLECTION_NAME)
    print("Collection loaded")

    # 日记数据
    diary_contents = [
        {
            "id": "diary_001",
            "content": "今天天气很好，去公园散步了，心情愉快。",
            "date": "2026-01-10",
            "mood": "happy",
            "tags": ["生活", "散步"],
        },
        {
            "id": "diary_002",
            "content": "今天工作很忙，完成了项目里程碑。",
            "date": "2026-01-11",
            "mood": "excited",
            "tags": ["工作", "成就"],
        },
        {
            "id": "diary_003",
            "content": "周末和朋友去爬山，很放松。",
            "date": "2026-01-12",
            "mood": "relaxed",
            "tags": ["户外", "朋友"],
        },
        {
            "id": "diary_004",
            "content": "今天学习了 Milvus 向量数据库。",
            "date": "2026-01-12",
            "mood": "curious",
            "tags": ["学习", "技术"],
        },
        {
            "id": "diary_005",
            "content": "晚上做了一顿晚餐，家人很喜欢。",
            "date": "2026-01-13",
            "mood": "proud",
            "tags": ["美食", "家庭"],
        },
    ]

    # 生成 embedding 并插入
    print("\nGenerating embeddings...")
    diary_data = []
    for diary in diary_contents:
      vector = get_embedding(diary["content"])
      diary_data.append({**diary, "vector": vector})

    print("Inserting data...")
    insert_result = client.insert(
        collection_name=COLLECTION_NAME,
        data=diary_data,
    )
    insert_count = insert_result.get("insert_count", insert_result.get("insert_cnt", 0))
    print(f"✓ Inserted {insert_count} records\n")

  except Exception as e:
    print("Error:", str(e))


if __name__ == '__main__':
  main()
