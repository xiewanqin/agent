import os
from dotenv import load_dotenv
from pymilvus import (
    connections, FieldSchema, CollectionSchema, DataType, Collection
)
from langchain_community.embeddings import DashScopeEmbeddings

load_dotenv()

COLLECTION_NAME = "ai_diary2"
VECTOR_DIM = 1024

# 1️⃣ embedding（DashScope 原生接口，比 OpenAI 兼容模式更稳定）
embeddings = DashScopeEmbeddings(
    dashscope_api_key=os.getenv("OPENAI_API_KEY"),
    model=os.getenv("EMBEDDINGS_MODEL_NAME", "text-embedding-v3"),
)


def get_embedding(text: str):
  return embeddings.embed_query(text)


def main():
  try:
    print("Connecting to Milvus...")
    connections.connect("default", host="localhost", port="19530")
    print("✓ Connected\n")

    # 2️⃣ 创建 collection（等价 JS fields）
    print("Creating collection...")

    fields = [
        FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=50),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIM),
        FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=5000),
        FieldSchema(name="date", dtype=DataType.VARCHAR, max_length=50),
        FieldSchema(name="mood", dtype=DataType.VARCHAR, max_length=50),
        FieldSchema(
            name="tags",
            dtype=DataType.ARRAY,
            element_type=DataType.VARCHAR,
            max_capacity=10,
            max_length=50
        )
    ]

    schema = CollectionSchema(fields, description="AI diary")

    collection = Collection(
        name=COLLECTION_NAME,
        schema=schema
    )

    print("Collection created")

    # 3️⃣ 创建索引（等价 IVF_FLAT + COSINE）
    print("\nCreating index...")
    collection.create_index(
        field_name="vector",
        index_params={
            "index_type": "IVF_FLAT",
            "metric_type": "COSINE",
            "params": {"nlist": 1024}
        }
    )
    print("Index created")

    # 4️⃣ load collection
    print("\nLoading collection...")
    collection.load()
    print("Collection loaded")

    # 5️⃣ 日记数据
    diary_contents = [
        {
            "id": "diary_001",
            "content": "今天天气很好，去公园散步了，心情愉快。",
            "date": "2026-01-10",
            "mood": "happy",
            "tags": ["生活", "散步"]
        },
        {
            "id": "diary_002",
            "content": "今天工作很忙，完成了项目里程碑。",
            "date": "2026-01-11",
            "mood": "excited",
            "tags": ["工作", "成就"]
        },
        {
            "id": "diary_003",
            "content": "周末和朋友去爬山，很放松。",
            "date": "2026-01-12",
            "mood": "relaxed",
            "tags": ["户外", "朋友"]
        },
        {
            "id": "diary_004",
            "content": "今天学习了 Milvus 向量数据库。",
            "date": "2026-01-12",
            "mood": "curious",
            "tags": ["学习", "技术"]
        },
        {
            "id": "diary_005",
            "content": "晚上做了一顿晚餐，家人很喜欢。",
            "date": "2026-01-13",
            "mood": "proud",
            "tags": ["美食", "家庭"]
        }
    ]

    # 6️⃣ embedding
    print("\nGenerating embeddings...")
    for diary in diary_contents:
      diary["vector"] = get_embedding(diary["content"])

    # 7️⃣ 插入
    print("Inserting data...")
    insert_result = collection.insert(diary_contents)

    print(f"✓ Inserted {len(insert_result.primary_keys)} records\n")

    # 8️⃣ flush（Python 必须）
    collection.flush()

  except Exception as e:
    print("Error:", str(e))


if __name__ == "__main__":
  main()
