import os
from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda, RunnableSequence, chain


load_dotenv()

add_one = RunnableLambda(lambda input: input + 1)
multiply_two = RunnableLambda(lambda input: input * 2)


@chain
def minus_three(input):
  return input - 3


# chain1 = RunnableSequence(
#     add_one,
#     multiply_two,
#     add_one,
#     minus_three,
#     lambda input: input *
#     input)

chain1 = add_one | multiply_two | minus_three | (lambda input: input * input)

result = chain1.invoke(5)
print(result)
