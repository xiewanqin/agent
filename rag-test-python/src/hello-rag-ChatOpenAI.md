下面是这段 RAG（检索增强生成）示例代码的逐段说明。

## 整体功能

这是一个基于 LangChain 的 RAG 示例，用“光光和东东”的故事做检索，再让大模型根据检索到的片段回答问题。

---

## 1. 导入与配置（第 1–9 行）

```python
import asyncio
import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()
```

- `asyncio`：异步执行
- `load_dotenv()`：从 `.env` 加载环境变量（API Key、模型名等）
- `Document`：LangChain 文档结构，包含 `page_content` 和 `metadata`
- `InMemoryVectorStore`：内存向量库，用于存储和检索文档向量
- `ChatOpenAI`、`OpenAIEmbeddings`：对话模型和文本嵌入模型

---

## 2. 模型初始化（第 11–23 行）

```python
model = ChatOpenAI(...)   # 对话模型
embeddings = OpenAIEmbeddings(...)  # 嵌入模型
```

- **ChatOpenAI**：用于生成回答，`temperature=0` 表示输出更稳定
- **OpenAIEmbeddings**：把文本转成向量，用于相似度检索
  - `check_embedding_ctx_length=False`：关闭上下文长度检查，适配 Dashscope 等只接受纯文本的接口

---

## 3. 文档数据（第 25–55 行）

```python
documents = [
    Document(page_content="...", metadata={"chapter": 1, "character": "光光", ...}),
    ...
]
```

- 7 个 `Document`，对应故事 7 个片段
- `page_content`：正文
- `metadata`：章节、角色、类型、心情等元信息，便于筛选和展示

---

## 4. 主流程 `main()`（第 58–109 行）

### 4.1 创建向量存储（第 59–62 行）

```python
vector_store = await InMemoryVectorStore.afrom_documents(documents, embeddings)
```

- 用 `embeddings` 把所有文档转成向量
- 存入内存向量库，供后续相似度检索

### 4.2 配置检索器（第 64 行）

```python
retriever = vector_store.as_retriever(search_kwargs={"k": 3})
```

- `k=3`：每次检索返回相似度最高的 3 个文档

### 4.3 检索与评分（第 74–90 行）

```python
retrieved_docs = await retriever.ainvoke(question)  # 方式1：只取文档
scored_results = await vector_store.asimilarity_search_with_score(question, k=3)  # 方式2：带分数
```

- `retriever.ainvoke`：按问题检索，返回文档列表
- `asimilarity_search_with_score`：返回 `(文档, 分数)` 列表
  - 分数为余弦相似度，0~1，越高越相似

### 4.4 构建 Prompt 并生成回答（第 92–108 行）

```python
context = "\n\n━━━━━\n\n".join(
    f"[片段{i + 1}]\n{doc.page_content}" for i, doc in enumerate(retrieved_docs)
)
prompt = f"""你是一个讲友情故事的老师。基于以下故事片段回答问题...
故事片段:
{context}
问题: {question}
老师的回答:"""
response = await model.ainvoke(prompt)
```

- 把检索到的 3 个片段拼成 `context`
- 在 prompt 中说明角色、任务、故事片段和问题
- 调用 `model.ainvoke` 生成回答

---

## 5. RAG 流程概览

```
用户问题 → 嵌入为向量 → 在向量库中检索 Top-K 文档 → 将文档作为上下文 → 大模型生成回答
```

---

## 6. 程序入口（第 112–113 行）

```python
if __name__ == "__main__":
  asyncio.run(main())
```

- 使用 `asyncio.run()` 运行异步 `main()` 函数

---

## 总结

这段代码演示了 RAG 的典型流程：用向量检索找到相关文档，再把这些文档作为上下文交给大模型回答。示例中用的是内存向量库和预设故事文档，实际项目中通常会换成持久化向量库（如 Chroma、Pinecone）和真实数据源。
