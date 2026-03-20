import os
from dotenv import load_dotenv
from pymilvus import MilvusClient, DataType
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ebooklib import epub, ITEM_DOCUMENT
import html2text

load_dotenv()

COLLECTION_NAME = 'ebook_collection1'
VECTOR_DIM = 1024
CHUNK_SIZE = 500
EPUB_FILE = './天龙八部.epub'

# 从文件名提取书名（去掉扩展名）
BOOK_NAME = os.path.splitext(os.path.basename(EPUB_FILE))[0]

embeddings = DashScopeEmbeddings(
    dashscope_api_key=os.getenv("OPENAI_API_KEY"),
    model=os.getenv("EMBEDDINGS_MODEL_NAME", "text-embedding-v3"),
)
milvus_uri = os.getenv("MILVUS_ADDRESS", "localhost:19530")
if not milvus_uri.startswith("http"):
  milvus_uri = f"http://{milvus_uri}"
client = MilvusClient(uri=milvus_uri)


def ensure_collection(book_id: int):
  if not client.has_collection(collection_name=COLLECTION_NAME):
    schema = MilvusClient.create_schema(auto_id=False, enable_dynamic_field=False)
    schema.add_field(
        field_name='id',
        datatype=DataType.INT64,
        is_primary=True)
    schema.add_field(
        field_name='vector',
        datatype=DataType.FLOAT_VECTOR,
        dim=VECTOR_DIM)
    schema.add_field(field_name='content', datatype=DataType.VARCHAR, max_length=10000)
    schema.add_field(field_name='book_id', datatype=DataType.INT64)
    schema.add_field(field_name='book_name', datatype=DataType.VARCHAR, max_length=200)
    schema.add_field(field_name='chapter_num', datatype=DataType.INT32)
    schema.add_field(field_name='index', datatype=DataType.INT32)

    client.create_collection(collection_name=COLLECTION_NAME, schema=schema)

    index_params = client.prepare_index_params()
    index_params.add_index(
        field_name='vector',
        index_type="IVF_FLAT",
        metric_type='COSINE',
        params={'nlist': 1024})
    client.create_index(collection_name=COLLECTION_NAME, index_params=index_params)
    print('✓ 索引创建成功')

    print('加载集合...')
    client.load_collection(collection_name=COLLECTION_NAME)
    print('✓ 集合已加载')

# ========================
# 加载 EPUB + 流式处理
# ========================


def load_and_process_epub(book_id):
  print(f"\n开始加载 EPUB: {EPUB_FILE}")

  book = epub.read_epub(EPUB_FILE)
  h2t = html2text.HTML2Text()
  h2t.ignore_links = True
  h2t.ignore_images = True

  # 按 spine 顺序获取章节
  chapters = []
  for item_id, _ in book.spine:
    item = book.get_item_with_id(item_id)
    if item and item.get_type() == ITEM_DOCUMENT:
      html_content = item.get_content().decode("utf-8", errors="ignore")
      text = h2t.handle(html_content).strip()
      if text:
        chapters.append(text)

  print(f"✓ 加载完成，共 {len(chapters)} 个章节\n")

  splitter = RecursiveCharacterTextSplitter(
      chunk_size=CHUNK_SIZE,
      chunk_overlap=50
  )

  total_inserted = 0

  for i, text in enumerate(chapters):
    title = f"第 {i + 1} 章"
    print(f"处理第 {i + 1}/{len(chapters)} 章...")

    chunks = splitter.split_text(text)

    print(f"  拆分为 {len(chunks)} 个片段")

    if not chunks:
      print("  跳过\n")
      continue
    # 加章节标题前缀
    chunks = [f"{title}\n{chunk}" for chunk in chunks]

    # 批量 embedding
    vectors = embeddings.embed_documents(chunks)
    data = []
    for j, (chunk, vector) in enumerate(zip(chunks, vectors)):
      data.append({
          "id": total_inserted + j,
          "book_id": book_id,
          "book_name": BOOK_NAME,
          "chapter_num": i + 1,
          "index": j,
          "content": chunk[:10000],
          "vector": vector
      })

    res = client.insert(
        collection_name=COLLECTION_NAME,
        data=data
    )
    cnt = res.get("insert_count", res.get("insert_cnt", len(data)))
    total_inserted += cnt

    print(f"  ✓ 插入 {cnt} 条（累计 {total_inserted}）")

  print(f"\n总共插入 {total_inserted} 条")
  return total_inserted


def main():
  try:
    print('=' * 80)
    print('电子书处理程序')
    print('=' * 80)

    ensure_collection(book_id=1)

    load_and_process_epub(book_id=1)

    print('=' * 80)
    print('处理完成！')
    print('=' * 80)

  except Exception as e:
    print(f'Error: {e}')


if __name__ == '__main__':
  main()
