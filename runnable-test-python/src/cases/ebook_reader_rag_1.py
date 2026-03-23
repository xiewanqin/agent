"""
对应 runnable-test/src/cases/ebook-reader-rag.mjs

Milvus 检索 + PromptTemplate + ChatOpenAI + StrOutputParser 的 RAG Runnable 链。
"""
from __future__ import annotations

import os
import asyncio
from typing import Any

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableSequence
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pymilvus import MilvusClient

load_dotenv()

COLLECTION_NAME = os.getenv("MILVUS_EBOOK_COLLECTION", "ebook_collection")
VECTOR_DIM = 1024

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.7,
    base_url=os.getenv("OPENAI_BASE_URL"),
)

embeddings = OpenAIEmbeddings(
    api_key=os.getenv("OPENAI_API_KEY"),
    model=os.getenv("EMBEDDINGS_MODEL_NAME", "text-embedding-3-small"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    dimensions=VECTOR_DIM,
)

_milvus_uri = os.getenv("MILVUS_ADDRESS", "localhost:19530")
if not _milvus_uri.startswith("http"):
  _milvus_uri = f"http://{_milvus_uri}"
milvus_client = MilvusClient(uri=_milvus_uri)


def _normalize_hit(hit: dict[str, Any], idx: int) -> dict[str, Any]:
  ent = hit.get("entity") if isinstance(hit.get("entity"), dict) else hit
  score = hit.get("score")
  if score is None:
    score = hit.get("distance")
  if not isinstance(ent, dict):
    ent = {}
  index_val = ent.get("index")
  if index_val is None:
    index_val = idx
  return {
      "id": ent.get("id"),
      "book_id": ent.get("book_id"),
      "chapter_num": ent.get("chapter_num"),
      "index": index_val,
      "content": ent.get("content") or "",
      "score": score,
  }


def milvus_search_fn(input: dict[str, Any]) -> dict[str, Any]:
  question = input["question"]
  k = int(input.get("k", 5))
  try:
    query_vector = embeddings.embed_query(question)
    raw = milvus_client.search(
        collection_name=COLLECTION_NAME,
        data=[query_vector],
        anns_field="vector",
        limit=k,
        search_params={"metric_type": "COSINE"},
        output_fields=["id", "book_id", "chapter_num", "index", "content"],
    )
    rows = raw[0] if raw else []
    retrieved = [_normalize_hit(row, i) for i, row in enumerate(rows)]
    return {"question": question, "retrievedContent": retrieved}
  except Exception as e:
    print(f"检索内容时出错: {e}")
    return {"question": question, "retrievedContent": []}


milvus_search = RunnableLambda(milvus_search_fn)

prompt_template = PromptTemplate.from_template(
    """你是一个专业的《天龙八部》小说助手。基于小说内容回答问题，用准确、详细的语言。

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
)


def build_prompt_input_fn(input: dict[str, Any]) -> dict[str, Any]:
  question = input["question"]
  retrieved_content = input.get("retrievedContent") or []

  if not retrieved_content:
    return {
        "hasContext": False,
        "question": question,
        "context": "",
        "retrievedContent": retrieved_content,
    }

  print("=" * 80)
  print(f"问题: {question}")
  print("=" * 80)
  print("\n【检索相关内容】")

  for i, item in enumerate(retrieved_content):
    print(f"\n[片段 {i + 1}] 相似度: {item.get('score', 'N/A')}")
    print(f"书籍: {item.get('book_id')}")
    print(f"章节: 第 {item.get('chapter_num')} 章")
    print(f"片段索引: {item.get('index')}")
    content = item.get("content") or ""
    preview = content[:200] + ("..." if len(content) > 200 else "")
    print(f"内容: {preview}")

  context = "\n\n━━━━━\n\n".join(
      f"[片段 {i + 1}]\n章节: 第 {item.get('chapter_num')} 章\n内容: {item.get('content', '')}"
      for i, item in enumerate(retrieved_content)
  )

  return {
      "hasContext": True,
      "question": question,
      "context": context,
      "retrievedContent": retrieved_content,
  }


build_prompt_input = RunnableLambda(build_prompt_input_fn)


def branch_context_fn(input: dict[str, Any]) -> dict[str, Any]:
  has_context = input.get("hasContext")
  question = input["question"]
  context = input.get("context") or ""

  if not has_context:
    fallback = "抱歉，我没有找到相关的《天龙八部》内容。请尝试换一个问题。"
    print(fallback)
    return {
        "question": question,
        "context": "",
        "answer": fallback,
        "noContext": True,
    }

  return {"question": question, "context": context, "noContext": False}


branch_context = RunnableLambda(branch_context_fn)

rag_chain = RunnableSequence(
    milvus_search,
    build_prompt_input,
    branch_context,
    prompt_template,
    model,
    StrOutputParser(),
)


def init_milvus_collection() -> None:
  print("连接到 Milvus...")
  print("✓ 已连接\n")
  try:
    milvus_client.load_collection(collection_name=COLLECTION_NAME)
    print("✓ 集合已加载\n")
  except Exception as e:
    msg = str(e).lower()
    if "already" in msg or "loaded" in msg:
      print("✓ 集合已处于加载状态\n")
    else:
      raise


async def main() -> None:
  try:
    init_milvus_collection()

    data = {
        "question": "鸠摩智会什么武功？",
        "k": 5,
    }

    print("=" * 80)
    print(f"问题: {data['question']}")
    print("=" * 80)
    print("\n【AI 流式回答】\n")

    async for chunk in rag_chain.astream(data):
      if chunk:
        print(chunk, end="", flush=True)

    print("\n")
  except Exception as e:
    print(f"错误: {e}")


if __name__ == "__main__":
  asyncio.run(main())
