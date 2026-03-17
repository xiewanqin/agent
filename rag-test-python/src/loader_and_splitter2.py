"""
网页加载 + 分割 + 完整 RAG 流程
对应 JS 版：loader-and-splitter2.mjs
"""

import asyncio
import os

import bs4
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.agents import create_agent
from langchain_core.documents import Document

load_dotenv()

model = init_chat_model(
    f"openai:{os.getenv('MODEL_NAME')}",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

embeddings = OpenAIEmbeddings(
    api_key=os.getenv("OPENAI_API_KEY"),
    model=os.getenv("EMBEDDINGS_MODEL_NAME"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    check_embedding_ctx_length=False,
)


async def main():
  # print("正在加载网页内容...")
  # loader = WebBaseLoader(
  #     web_paths=["https://juejin.cn/post/7233327509919547452"],
  #     bs_kwargs={"parse_only": bs4.SoupStrainer(["p", "title"])},
  # )
  # documents = loader.load()
  # print(f"加载完成，总字符数: {len(documents[0].page_content)}\n")

  text = "12，123，456。12345678901234。"
  documents = [Document(page_content=text, metadata={})]

  text_splitter = RecursiveCharacterTextSplitter(
      chunk_size=9,
      chunk_overlap=4,
      separators=["。", "！", "？"],
      add_start_index=True,
  )
  split_documents = text_splitter.split_documents(documents)
  for i, doc in enumerate(split_documents):
    print(f"chunk[{i + 1}]: {doc}")
    print()
#   print(f"文档分割完成，共 {len(split_documents)} 个分块\n")

#   print("正在创建向量存储...")
#   vector_store = await InMemoryVectorStore.afrom_documents(split_documents, embeddings)
#   print("向量存储创建完成\n")

#   questions = ["父亲的去世对作者的人生态度产生了怎样的根本性逆转？"]

#   for question in questions:
#     print("=" * 80)
#     print(f"问题: {question}")
#     print("=" * 80)

#     # similarity_search_with_score 一次调用同时获取文档和相似度评分
#     scored_results = await vector_store.asimilarity_search_with_score(question, k=2)

#     retrieved_docs = [doc for doc, _ in scored_results]

#     print("\n【检索到的文档及相似度评分】")
#     for i, (doc, score) in enumerate(scored_results):
#       print(f"\n[文档 {i + 1}] 相似度: {score:.4f}")
#       print(f"内容: {doc.page_content}")
#       if doc.metadata:
#         print(f"元数据: {doc.metadata}")

#     context = "\n\n━━━━━\n\n".join(
#         f"[片段{i + 1}]\n{doc.page_content}" for i, doc in enumerate(retrieved_docs)
#     )

#     prompt = f"""你是一个文章辅助阅读助手，根据文章内容来解答：

# 文章内容：
# {context}

# 问题: {question}

# 你的回答:"""

#     print("\n【AI 回答】")

#     graph = create_agent(
#         model=model,
#         # system_prompt=prompt,
#     )
#     response = await graph.ainvoke({"messages": [{"role": "user", "content": prompt}]})
#     print(response["messages"][-1].content)
#     print()

if __name__ == "__main__":
  asyncio.run(main())
