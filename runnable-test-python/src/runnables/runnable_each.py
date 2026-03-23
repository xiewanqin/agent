from langchain_core.runnables import RunnableLambda, RunnableSequence
from langchain_core.runnables.base import RunnableEach


def to_upper(input):
  return input.upper()


def add_greeting(input):
  return f"你好，{input}！"


process_item = RunnableSequence(
    to_upper,
    add_greeting,
)

chain = RunnableEach(
    bound=process_item,
)

input = ["alice", "bob", "carol"]
result = chain.invoke(input)
print(f"RunnableEach - 数组元素处理:")
print(f"输入: {input}")
print(f"输出: {result}")
