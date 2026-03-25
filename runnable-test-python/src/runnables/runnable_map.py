import os
from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda, RunnableMap, chain
from langchain_core.prompts import PromptTemplate

load_dotenv()

add_one = RunnableLambda(lambda input: input['num'] + 1)
multiply_two = RunnableLambda(lambda input: input['num'] * 2)


@chain
def square(input):
  return input['num'] * input['num']


greet_template = PromptTemplate.from_template("你好，{name}！")
weather_template = PromptTemplate.from_template("今天天气{weather}。")

runnable_map = RunnableMap({
    "add": add_one,
    "multiply": multiply_two,
    "square": square,
    "greet": greet_template,
    "weather": weather_template,
})

result = runnable_map.invoke({
    "name": "小西",
    "weather": "多云",
    'num': 5,
})
print(result)
