import os
from dotenv import load_dotenv
from langchain_core.runnables import RunnableBranch, RunnableLambda

load_dotenv()

is_positive = RunnableLambda(lambda input: input > 0)
is_negative = RunnableLambda(lambda input: input < 0)
is_even = RunnableLambda(lambda input: input % 2 == 0)

handle_positive = RunnableLambda(lambda input: f"正数: {input} + 10 = {input + 10}")
handle_negative = RunnableLambda(lambda input: f"负数: {input} - 10 = {input - 10}")
handle_even = RunnableLambda(lambda input: f"偶数: {input} * 2 = {input * 2}")
handle_default = RunnableLambda(lambda input: f"默认: {input}")

branch = RunnableBranch(
    (is_positive, handle_positive),
    (is_negative, handle_negative),
    # (is_even, handle_even),
    handle_default,
)

test_cases = [5, -3, 4, 0]
for test_case in test_cases:
  result = branch.invoke(test_case)
  print(f"输入: {test_case} => {result}")
