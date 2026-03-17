这是一个完整的 **RAG（检索增强生成）** 示例，整体可以分为 4 个阶段：

---

## 第一阶段：初始化（1~57 行）

```
初始化了 3 样东西：
  model      → 负责"理解问题、生成回答"的大语言模型（LLM）
  embeddings → 负责"把文字转成向量"的嵌入模型
  documents  → 7 段光光与东东的故事，每段带 metadata（章节/角色/类型/心情）
```

**`model` 和 `embeddings` 是两个不同的模型：**

- `model`（`qwen-plus`）：对话模型，负责最终回答问题
- `embeddings`（`text-embedding-v3`）：嵌入模型，专门把文本转成高维数字向量，不参与对话，只做"语义相似度计算"

---

## 第二阶段：建库（62 行）

```57:63:rag-test-python/src/hello_rag.py
async def main():
  print("正在创建向量存储...")
  vector_store = await InMemoryVectorStore.afrom_documents(documents, embeddings)
  print("向量存储创建完成\n")
```

`afrom_documents` 做了两件事：

1. 调用 `embeddings` 模型，把 7 段故事**每一段都转成一个向量**（一串浮点数，代表这段文字的"语义坐标"）
2. 把 `文本 + 向量 + metadata` 全部存入内存向量库 `InMemoryVectorStore`

内存中的状态变成：

```
向量库
├── [向量①] "光光是一个活泼开朗的小男孩..."  → metadata: {chapter:1, ...}
├── [向量②] "东东是光光最好的朋友..."         → metadata: {chapter:2, ...}
├── ...
└── [向量⑦] "多年后，光光成为了一名职业..."   → metadata: {chapter:7, ...}
```

---

## 第三阶段：把检索包装成 Tool（67~93 行）

```67:93:rag-test-python/src/hello_rag.py
  @tool
  async def search_story(query: str) -> str:
    """根据问题从故事中检索最相关的片段，用于回答关于光光和东东故事的问题"""
    scored_results = await vector_store.asimilarity_search_with_score(query, k=3)
    ...
    return "\n\n━━━━━\n\n".join(result_parts)

  graph = create_agent(
      model=model,
      tools=[search_story],
      prompt="你是一个讲友情故事的老师...",
  )
```

**`@tool` 的作用：** 把普通函数变成 Agent 可以调用的工具。`create_agent` 内部会自动把 `search_story` 的签名和 docstring 告诉 LLM，LLM 看到 docstring 就知道"这个工具能干什么、什么时候该用它"。

**`asimilarity_search_with_score` 的原理：**

```
用户问题  ──→  embeddings 转成向量  ──→  和库里 7 个向量做余弦相似度计算
                                         ──→  返回最相似的 3 段（k=3）及评分
```

评分是余弦相似度（0~1），越接近 1 代表语义越相近。

**`create_agent` 做了什么：**

- 创建了一个基于 LangGraph 的 ReAct Agent
- 自动把 `search_story` 绑定到 model（`model.bind_tools`），不需要你手动处理
- 返回一个可运行的 `graph`（状态机）

---

## 第四阶段：Agent 运行（95~121 行）

```95:121:rag-test-python/src/hello_rag.py
  questions = ["东东和光光是怎么成为朋友的？"]

  for question in questions:
    ...
    inputs = {"messages": [{"role": "user", "content": question}]}

    async for chunk in graph.astream(inputs, stream_mode="values"):
      ...
      if hasattr(last, "tool_calls") and last.tool_calls:
        for tc in last.tool_calls:
          print(f"\n🤖 AI 决定调用: [{tc['name']}]  参数: {tc['args']}")
```

Agent 的运行是一个**自动循环**，底层流程是：

```
用户问题
  ↓
【model 节点】LLM 分析问题，决定要不要调工具
  ↓ 决定调 search_story
【tools 节点】执行 search_story，从向量库检索 3 段相关故事
  ↓ 把检索结果返回给 LLM
【model 节点】LLM 拿到故事片段，生成最终回答
  ↓
输出答案
```

`astream(stream_mode="values")` 是流式输出，每走完一个节点就推送一次 `chunk`，所以代码里实时打印了"AI 决定调用哪个工具"的过程，而不是等全部跑完才输出。

---

**整体一句话总结：** 把 7 段故事向量化存库 → 把检索包装成 Tool → Agent 收到问题后自主决定去检索哪些片段 → 用检索到的内容生成回答。这就是 **RAG** 的完整链路。
