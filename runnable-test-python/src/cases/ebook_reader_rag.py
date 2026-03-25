"""
Milvus + DashScope Embeddings + ChatOpenAI 的 RAG Runnable 链。
"""
from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from pymilvus import MilvusClient

load_dotenv()

COLLECTION_NAME = os.getenv("MILVUS_EBOOK_COLLECTION", "ebook_collection1")


class MilvusRetriever:
  """封装 Milvus 向量检索。"""

  def __init__(self, uri: str, collection_name: str, embeddings_model: Any) -> None:
    self.client = MilvusClient(uri=uri)
    self.collection_name = collection_name
    self.embeddings_model = embeddings_model

  def load_collection(self) -> None:
    if not self.client.has_collection(self.collection_name):
      raise ValueError(f"集合 {self.collection_name} 不存在，请先写入数据")
    self.client.load_collection(collection_name=self.collection_name)
    print(f"✓ 集合 '{self.collection_name}' 已加载")

  def search(self, query: str, k: int = 5) -> list[dict[str, Any]]:
    """返回检索到的片段列表；失败时返回空列表。"""
    try:
      query_vector = self.embeddings_model.embed_query(query)
      batch = self.client.search(
          collection_name=self.collection_name,
          data=[query_vector],
          anns_field="vector",
          limit=k,
          search_params={"metric_type": "COSINE"},
          output_fields=["id", "book_id", "chapter_num", "index", "content"],
      )
      rows = batch[0] if batch else []
      out: list[dict[str, Any]] = []
      for idx, row in enumerate(rows):
        ent = row.get("entity") if isinstance(row.get("entity"), dict) else row
        if not isinstance(ent, dict):
          ent = {}
        raw_index = ent.get("index")
        out.append(
            {
                "id": ent.get("id"),
                "book_id": ent.get("book_id"),
                "chapter_num": ent.get("chapter_num"),
                "index": idx if raw_index is None else raw_index,
                "content": ent.get("content") or "",
                "score": row.get("distance", row.get("score")),
            }
        )
      return out
    except Exception as e:
      print(f"搜索时出错: {e}")
      return []


def milvus_search_step(
    input_data: dict[str, Any], *, retriever: MilvusRetriever
) -> dict[str, Any]:
  question = input_data.get("question") or ""
  k = int(input_data.get("k", 5))
  retrieved = retriever.search(question, k)
  return {"question": question, "retrieved_content": retrieved}


def build_prompt_input_fn(input_data: dict[str, Any]) -> dict[str, Any]:
  question = input_data.get("question")
  retrieved_content = input_data.get("retrieved_content") or []
  if not retrieved_content:
    return {
        "has_context": False,
        "question": question,
        "context": "",
        "retrieved_content": [],
    }

  print("=" * 80)
  print(f"问题: {question}")
  print("=" * 80)
  print("\n【检索相关内容】")

  for idx, item in enumerate(retrieved_content):
    print(f"\n[片段 {idx + 1}] 相似度: {item.get('score', 'N/A')}")
    print(f"书籍: {item.get('book_id')}")
    print(f"章节: 第 {item.get('chapter_num')} 章")
    print(f"片段索引: {item.get('index')}")
    content = item.get("content") or ""
    preview = content[:200] + ("..." if len(content) > 200 else "")
    print(f"内容: {preview}")

  context = "\n\n━━━━━\n\n".join(
      f"[片段 {i + 1}]\n章节: 第 {it.get('chapter_num')} 章\n内容: {it.get('content', '')}"
      for i, it in enumerate(retrieved_content)
  )
  return {
      "has_context": True,
      "question": question,
      "context": context,
      "retrieved_content": retrieved_content,
  }


def check_context_fn(input_data: dict[str, Any]) -> dict[str, Any]:
  has_context = bool(input_data.get("has_context"))
  question = input_data.get("question")
  context = input_data.get("context") or ""

  if not has_context:
    fallback = "抱歉，我没有找到相关的《天龙八部》内容。请尝试换一个问题。"
    print(fallback)
    return {
        "question": question,
        "context": "",
        "answer": fallback,
        "no_context": True,
    }

  return {"question": question, "context": context, "no_context": False}


PROMPT_TEXT = """你是一个专业的《天龙八部》小说助手。基于小说内容回答问题，用准确、详细的语言。

请根据以下《天龙八部》小说片段内容回答问题：
{context}

用户问题: {question}

回答要求：
1. 如果片段中有相关信息，请结合小说内容给出详细、准确的回答
2. 可以综合多个片段的内容，提供完整的答案
3. 如果片段中没有相关信息，请如实告知用户
4. 回答要准确，符合小说的情节和人物设定
5. 可以引用原文内容来支持你的回答

AI 助手的回答:"""


def main() -> None:
  retriever: MilvusRetriever | None = None
  try:
    print("初始化 RAG 系统...\n")
    milvus_uri = os.getenv("MILVUS_URI", "http://localhost:19530")
    if not milvus_uri.startswith("http"):
      milvus_uri = f"http://{milvus_uri}"

    model = ChatOpenAI(
        model=os.getenv("MODEL_NAME"),
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7,
        base_url=os.getenv("OPENAI_BASE_URL"),
    )

    embeddings = DashScopeEmbeddings(
        model=os.getenv("EMBEDDINGS_MODEL_NAME", "text-embedding-v3"),
        dashscope_api_key=os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY"),
    )

    print(f"连接到 Milvus: {milvus_uri}")
    retriever = MilvusRetriever(
        uri=milvus_uri,
        collection_name=COLLECTION_NAME,
        embeddings_model=embeddings,
    )
    retriever.load_collection()

    milvus_search = RunnableLambda(lambda x: milvus_search_step(x, retriever=retriever))
    build_prompt_input = RunnableLambda(build_prompt_input_fn)
    check_context = RunnableLambda(check_context_fn)
    prompt_template = PromptTemplate.from_template(PROMPT_TEXT)

    rag_chain = (
        milvus_search
        | build_prompt_input
        | check_context
        | prompt_template
        | model
        | StrOutputParser()
    )

    data: dict[str, Any] = {"question": "王语嫣喜欢谁", "k": 5}
    print("=" * 80)
    print(f"问题: {data['question']}")
    print("=" * 80)
    print("\n【AI 流式回答】\n")

    for chunk in rag_chain.stream(data):
      print(chunk, end="", flush=True)

    print("\n")
  except Exception as e:
    print(f"错误: {e}")
    raise
  finally:
    if retriever is not None:
      try:
        retriever.client.close()
      except Exception:
        pass
      print("✓ 已断开 Milvus 连接")


if __name__ == "__main__":
  main()
