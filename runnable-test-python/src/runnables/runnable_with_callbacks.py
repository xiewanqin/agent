"""
对应 runnable-test/src/runnables/RunnableWithCallbacks.mjs

文本处理链：清洗 → 分词 → 统计；用 BaseCallbackHandler 观测每一步。
"""
from __future__ import annotations

import json
import re
from typing import Any

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.runnables import RunnableLambda, RunnableSequence


def clean(text: str) -> str:
  return re.sub(r"\s+", " ", text.strip())


def tokenize(text: str) -> list[str]:
  return text.split()


def count(tokens: list[str]) -> dict[str, Any]:
  return {"tokens": tokens, "wordCount": len(tokens)}


class ChainStepLogger(BaseCallbackHandler):
  """等价于 mjs 里 handleChainStart / handleChainEnd / handleChainError。"""

  def on_chain_start(
      self,
      serialized: dict[str, Any] | None,
      inputs: dict[str, Any],
      *,
      run_id,
      tags: list[str] | None = None,
      name: str | None = None,
      **kwargs: Any,
  ) -> None:
    step = name or (tags[-1] if tags else "unknown")
    print(f"[START] {step}")

  def on_chain_end(
      self,
      outputs: Any,
      *,
      run_id,
      **kwargs: Any,
  ) -> None:
    try:
      out_str = json.dumps(outputs, ensure_ascii=False)
    except TypeError:
      out_str = repr(outputs)
    print(f"[END]   output={out_str}\n")

  def on_chain_error(
      self,
      error: BaseException,
      *,
      run_id,
      **kwargs: Any,
  ) -> None:
    print(f"[ERROR] {error!s}\n")


chain = RunnableSequence(
    RunnableLambda(clean),
    RunnableLambda(tokenize),
    RunnableLambda(count),
)


def main() -> None:
  result = chain.invoke(
      "  hello   world   from   langchain  ",
      config={"callbacks": [ChainStepLogger()]},
  )
  print("结果:", result)


if __name__ == "__main__":
  main()
