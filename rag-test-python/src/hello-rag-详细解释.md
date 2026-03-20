## 一、环境初始化

```1:9:rag-test-python/src/hello_rag.py
import asyncio
import os

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()
```

| 导入项                | 作用                                                                                      |
| --------------------- | ----------------------------------------------------------------------------------------- |
| `asyncio`             | Python 内置异步库，支持 `async/await` 协程，避免 API 调用时阻塞主线程                     |
| `os`                  | 读取环境变量                                                                              |
| `load_dotenv()`       | 读取 `.env` 文件，把里面的 KEY=VALUE 注入到 `os.environ`，保密信息不写死在代码中          |
| `Document`            | LangChain 标准文档格式，包含 `page_content`（正文）和 `metadata`（元数据字典）            |
| `InMemoryVectorStore` | 纯内存向量库，进程结束即销毁，适合学习/原型，不需要安装额外数据库                         |
| `ChatOpenAI`          | 封装 OpenAI Chat Completion API，也可对接兼容 OpenAI 协议的其他服务（如阿里云 Dashscope） |
| `OpenAIEmbeddings`    | 封装 OpenAI Embeddings API，把文本转成高维向量（浮点数组）                                |

---

## 二、ChatOpenAI 对话模型

```11:16:rag-test-python/src/hello_rag.py
model = ChatOpenAI(
    temperature=0,
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)
```

- **`temperature=0`**：控制输出随机性。0 = 最确定、最一致，接近 1 = 更有创意但可能飘。做问答类任务一般设为 0
- **`model`**：从 `.env` 读取，比如 `qwen-max`、`gpt-4o` 等
- **`base_url`**：允许把请求转发到非 OpenAI 的兼容接口（代理或国产模型）

---

## 三、OpenAIEmbeddings 嵌入模型

```18:24:rag-test-python/src/hello_rag.py
embeddings = OpenAIEmbeddings(
    api_key=os.getenv("OPENAI_API_KEY"),
    model=os.getenv("EMBEDDINGS_MODEL_NAME"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    # Dashscope 只接受纯文本，禁止 tiktoken 将文本编码为 token ID 再发送
    check_embedding_ctx_length=False,
)
```

- **嵌入（Embedding）是什么**：把一段文字转成一个高维向量（如 1536 维），语义相近的文本在向量空间中距离更近
- **`check_embedding_ctx_length=False`**：LangChain 默认会用 tiktoken 对文本做 token 计数并截断，但 Dashscope 的 embedding 接口只接受原始字符串，开启 tiktoken 编码会报错，所以关闭此检查
- **嵌入模型和对话模型是两个不同的模型**：嵌入模型用于检索，对话模型用于生成回答，两者可以来自不同提供商

---

## 四、文档数据集

```26:55:rag-test-python/src/hello_rag.py
documents = [
    Document(
        page_content="光光是一个活泼开朗的小男孩，...",
        metadata={"chapter": 1, "character": "光光", "type": "角色介绍", "mood": "活泼"},
    ),
    ...
]
```

这里手动构造了 7 个文档，代表故事的 7 个章节。实际项目中通常从文件、数据库或网页中加载。

`metadata` 的价值：

- 展示时可以展示章节、角色等信息
- 可以配合 `filter` 做**元数据过滤检索**，比如只检索 `chapter >= 3` 的文档
- 这里暂时只用于打印，没有做过滤

---

## 五、main() 异步主函数

### 5.1 创建向量存储

```59:62:rag-test-python/src/hello_rag.py
  print("正在创建向量存储...")
  // vector_store 是实例
  vector_store = await InMemoryVectorStore.afrom_documents(documents, embeddings)
  print("向量存储创建完成\n")
```

**内部发生了什么：**

1. 遍历 `documents` 列表
2. 对每个 `Document.page_content` 调用嵌入模型 API，获取向量
3. 把 `(向量, 文档)` 对存入内存字典
4. `afrom_documents` 是异步版本，不会阻塞，实际上是批量并发发请求

---

### 5.2 配置检索器

```64:64:rag-test-python/src/hello_rag.py
  retriever = vector_store.as_retriever(search_kwargs={"k": 3})
```

- `retriever` 是 LangChain 的统一检索接口，屏蔽了底层向量库的差异
- `k=3`：只返回相似度最高的 3 个文档（Top-K 检索）
- **为什么不返回全部**：避免把不相关的文档塞进 prompt，token 有限且无关信息会干扰回答质量

---

### 5.3 双重检索（含相似度分数）

```74:90:rag-test-python/src/hello_rag.py
    retrieved_docs = await retriever.ainvoke(question)

    scored_results = await vector_store.asimilarity_search_with_score(question, k=3)

    print("\n【检索到的文档及相似度评分】")
    for i, (doc, score) in enumerate(scored_results):
      print(f"\n[文档 {i + 1}] 相似度: {score:.4f}")
      print(f"内容: {doc.page_content}")
```

代码做了**两次检索**，目的不同：

| 方法                                      | 返回值                    | 用途                           |
| ----------------------------------------- | ------------------------- | ------------------------------ |
| `retriever.ainvoke(question)`             | `List[Document]`          | 用于拼接 prompt 上下文         |
| `asimilarity_search_with_score(question)` | `List[(Document, float)]` | 仅用于打印，方便调试和观察分数 |

**余弦相似度**：两个向量夹角的余弦值，范围 [0, 1]，越接近 1 表示语义越相似。检索时把问题也转成向量，然后计算与所有文档向量的余弦相似度，取最高的 K 个。

---

### 5.4 构建 Prompt

```92:104:rag-test-python/src/hello_rag.py
    context = "\n\n━━━━━\n\n".join(
        f"[片段{i + 1}]\n{doc.page_content}" for i, doc in enumerate(retrieved_docs)
    )

    prompt = f"""你是一个讲友情故事的老师。基于以下故事片段回答问题，用温暖生动的语言。如果故事中没有提到，就说"这个故事里还没有提到这个细节"。

故事片段:
{context}

问题: {question}

老师的回答:"""
```

**Prompt 工程技巧：**

1. **角色设定**：`"你是一个讲友情故事的老师"` — 引导模型以特定风格和口吻回答
2. **注入检索内容**：把 3 个片段用分隔线拼成 `context`，让模型有据可查
3. **兜底指令**：`"如果故事中没有提到，就说..."` — 防止模型"幻觉"，编造故事中没有的内容
4. **明确结束标记**：`老师的回答:` 后面不写内容，引导模型继续补全

**`context` 的结构示例：**

```
[片段1]
从那以后，光光和东东成为了学校里最要好的朋友...

━━━━━

[片段2]
有一天，学校要举办一场足球比赛...

━━━━━

[片段3]
东东是光光最好的朋友...
```

---

### 5.5 调用模型生成回答

```106:108:rag-test-python/src/hello_rag.py
    print("\n【AI 回答】")
    response = await model.ainvoke(prompt)
    print(response.content)
```

- `model.ainvoke(prompt)` 把整个 prompt 字符串发给对话模型
- 返回的 `response` 是 `AIMessage` 对象，`.content` 是纯文本回答

---

## 六、完整 RAG 数据流

```
问题字符串
    │
    ▼
【嵌入模型】把问题转成向量
    │
    ▼
【向量库】余弦相似度搜索 → Top-3 文档
    │
    ▼
【Prompt 构建】角色设定 + 检索内容 + 原始问题
    │
    ▼
【对话模型】理解上下文 → 生成回答
    │
    ▼
打印输出
```

---

## 七、关键设计思想

| 问题               | RAG 的解决方式                          |
| ------------------ | --------------------------------------- |
| 模型不知道私有数据 | 检索时动态注入相关片段                  |
| Token 窗口有限     | 只注入最相关的 Top-K 片段，不是全部文档 |
| 防止幻觉           | Prompt 中明确说"没有就说没有"           |
| 调试困难           | 打印相似度分数，可以直观看检索是否准确  |
