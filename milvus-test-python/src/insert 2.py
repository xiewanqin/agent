"""
Milvus 日记插入脚本 - Python 版本
对应 insert.mjs 的功能
"""
import os
from dotenv import load_dotenv
from pymilvus import MilvusClient, DataType
from langchain_openai import OpenAIEmbeddings

load_dotenv()

COLLECTION_NAME = "ai_diary"
VECTOR_DIM = 1024

embeddings = OpenAIEmbeddings(
    api_key=os.getenv("OPENAI_API_KEY"),
    model=os.getenv("EMBEDDINGS_MODEL_NAME"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    dimensions=VECTOR_DIM,
)

# Milvus Python 客户端使用 uri 格式，需要 http:// 前缀
milvus_uri = os.getenv("MILVUS_ADDRESS", "localhost:19530")
if not milvus_uri.startswith("http"):
    milvus_uri = f"http://{milvus_uri}"

client = MilvusClient(uri=milvus_uri)


def get_embedding(text: str) -> list[float]:
    """获取文本的向量嵌入"""
    return embeddings.embed_query(text)


def main():
    try:
        print("Connecting to Milvus...")
        # Python MilvusClient 连接是同步的，创建时即连接
        print("✓ Connected\n")

        # 若集合已存在则先删除（便于重复运行）
        if client.has_collection(COLLECTION_NAME):
            print(f"Dropping existing collection '{COLLECTION_NAME}'...")
            client.drop_collection(COLLECTION_NAME)

        # 创建集合
        print("Creating collection...")
        schema = MilvusClient.create_schema(
            auto_id=False,
            enable_dynamic_field=False,
        )
        schema.add_field(
            field_name="id",
            datatype=DataType.VARCHAR,
            max_length=50,
            is_primary=True,
        )
        schema.add_field(
            field_name="vector",
            datatype=DataType.FLOAT_VECTOR,
            dim=VECTOR_DIM,
        )
        schema.add_field(
            field_name="content",
            datatype=DataType.VARCHAR,
            max_length=5000,
        )
        schema.add_field(
            field_name="date",
            datatype=DataType.VARCHAR,
            max_length=50,
        )
        schema.add_field(
            field_name="mood",
            datatype=DataType.VARCHAR,
            max_length=50,
        )
        schema.add_field(
            field_name="tags",
            datatype=DataType.ARRAY,
            element_type=DataType.VARCHAR,
            max_capacity=10,
            max_length=50,
        )

        # 先创建集合（不传 index_params，避免自动索引冲突）
        client.create_collection(
            collection_name=COLLECTION_NAME,
            schema=schema,
        )
        print("Collection created")

        # 单独创建向量索引
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

        # 插入日记数据
        print("\nInserting diary entries...")
        diary_contents = [
            {
                "id": "diary_001",
                "content": "今天天气很好，去公园散步了，心情愉快。看到了很多花开了，春天真美好。",
                "date": "2026-01-10",
                "mood": "happy",
                "tags": ["生活", "散步"],
            },
            {
                "id": "diary_002",
                "content": "今天工作很忙，完成了一个重要的项目里程碑。团队合作很愉快，感觉很有成就感。",
                "date": "2026-01-11",
                "mood": "excited",
                "tags": ["工作", "成就"],
            },
            {
                "id": "diary_003",
                "content": "周末和朋友去爬山，天气很好，心情也很放松。享受大自然的感觉真好。",
                "date": "2026-01-12",
                "mood": "relaxed",
                "tags": ["户外", "朋友"],
            },
            {
                "id": "diary_004",
                "content": "今天学习了 Milvus 向量数据库，感觉很有意思。向量搜索技术真的很强大。",
                "date": "2026-01-12",
                "mood": "curious",
                "tags": ["学习", "技术"],
            },
            {
                "id": "diary_005",
                "content": "晚上做了一顿丰盛的晚餐，尝试了新菜谱。家人都说很好吃，很有成就感。",
                "date": "2026-01-13",
                "mood": "proud",
                "tags": ["美食", "家庭"],
            },
        ]

        print("Generating embeddings...")
        diary_data = []
        for diary in diary_contents:
            vector = get_embedding(diary["content"])
            diary_data.append(
                {
                    **diary,
                    "vector": vector,
                }
            )

        insert_result = client.insert(
            collection_name=COLLECTION_NAME,
            data=diary_data,
        )
        insert_count = insert_result.get("insert_count", insert_result.get("insert_cnt", 0))
        print(f"✓ Inserted {insert_count} records\n")

    except Exception as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
