import os
from dotenv import load_dotenv
from pymilvus import MilvusClient

load_dotenv()

COLLECTION_NAME = 'ai_diary4'

milvus_uri = os.getenv("MILVUS_ADDRESS", "localhost:19530")
if not milvus_uri.startswith("http"):
  milvus_uri = f"http://{milvus_uri}"
client = MilvusClient(uri=milvus_uri)


def main():
  try:
    print('Connecting to Milvus...')
    print('✓ Connected\n')

    print('Deleting diary entry...')
    delete_id = 'diary_001'
    result = client.delete(
        collection_name=COLLECTION_NAME,
        filter=f'id == "{delete_id}"'
    )
    print(f"✓ Deleted {result.get('delete_count')} record(s)")
    print(f"  ID: {delete_id}\n")

    print('Batch deleting diary entries...')
    delete_ids = ['diary_002', 'diary_003']
    result = client.delete(
        collection_name=COLLECTION_NAME,
        ids=delete_ids
    )
    print(f"✓ Batch deleted {result.get('delete_count')} record(s)")
    print(f"  IDs: {', '.join(delete_ids)}\n")

    print('Deleting by condition...')
    result = client.delete(
        collection_name=COLLECTION_NAME,
        filter=f'mood == "proud"'
    )
    print(f"✓ Deleted {result.get('delete_count')} record(s)")
    print(f"  Condition: mood == 'proud'\n")

  except Exception as e:
    print(f'Error: {e}')


if __name__ == '__main__':
  main()
