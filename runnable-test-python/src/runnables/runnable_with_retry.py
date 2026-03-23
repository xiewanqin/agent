"""
演示 RunnableLambda + with_retry：失败时按次数自动重试（基于 tenacity）。
"""
import random
from langchain_core.runnables import RunnableLambda


class SimulatedRandomFailure(RuntimeError):
  """仅用于本示例，便于区分「预期内的模拟失败」。"""


def make_unstable_runner(fail_probability: float = 0.8):
  """用闭包保存尝试次数，避免模块级 global。"""

  attempt = 0

  def unstable_runner(input: str) -> str:
    nonlocal attempt
    attempt += 1
    print(f"第 {attempt} 次尝试，输入: {input}")

    if random.random() < fail_probability:
      print("本次尝试失败，抛出错误。")
      raise SimulatedRandomFailure("模拟的随机错误")

    print("本次尝试成功。")
    return f"成功处理: {input}"

  return unstable_runner


def main() -> None:
  unstable_runnable = RunnableLambda(make_unstable_runner(0.8))
  result = unstable_runnable.with_retry(stop_after_attempt=5).invoke("演示 withRetry")
  print(result)


if __name__ == "__main__":
  main()
