from langchain_core.runnables import RunnableLambda

# 备选


def premium_translator(text):
  print("[Premium] 尝试翻译...")
  raise Exception("Premium 服务超时")


def standard_translator(text):
  print("[Standard] 尝试翻译...")
  return "xxx"
  # raise Exception("Standard 服务限流")


def local_translator(text):
  print("[Local] 使用本地词典翻译...")
  dict = {"hello": "你好", "world": "世界", "goodbye": "再见"}
  words = text.lower().split(" ")
  return " ".join([dict[w] if w in dict else w for w in words])


premium_translator = RunnableLambda(premium_translator)
standard_translator = RunnableLambda(standard_translator)
local_translator = RunnableLambda(local_translator)

translator = premium_translator.with_fallbacks(
    fallbacks=[standard_translator, local_translator])

result = translator.invoke("hello world")
print(result)
