已写好 **`runnable-test-python/src/runnables/runnable_with_callbacks.py`**，并与 mjs 行为对齐。

## 与 JS 的差异（重要）

| JS                                       | Python                                                                                          |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `callbacks: [{ handleChainStart, ... }]` | 需继承 **`BaseCallbackHandler`**，实现 **`on_chain_start` / `on_chain_end` / `on_chain_error`** |
| `chain.invoke(x, { callbacks })`         | **`chain.invoke(x, config={"callbacks": [handler]})`**                                          |
| `trim` + `/\s+/g` 合并空白               | **`re.sub(r"\s+", " ", text.strip())`**                                                         |
| `count` 返回 `{ tokens, wordCount }`     | 相同                                                                                            |

原先 Python 里把 **dict 当 callback** 传给 `invoke` 是无效的；LangChain Python 只认 **`BaseCallbackHandler` 实例**（或 `AsyncCallbackHandler` 等）。

## 运行

```bash
cd runnable-test-python && uv run python src/runnables/runnable_with_callbacks.py
```

日志里会看到每步的 `[START]` / `[END]`，以及最外层 `RunnableSequence` 多一次 `[END]`（与 Runnable 嵌套运行方式一致）。
