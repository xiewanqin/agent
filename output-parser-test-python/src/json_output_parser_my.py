import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)

parser = JsonOutputParser()

question = f"""请介绍一下爱因斯坦的信息。请以 JSON 格式返回，包含以下字段（键名必须与英文完全一致、无空格）：name、birth_year、nationality、major_achievements（数组）、famous_theory。

{parser.get_format_instructions()}"""

if __name__ == "__main__":
  print("question:", question)
  try:
    print("🤔 正在调用大模型（使用 JsonOutputParser）...\n")

    response = model.invoke(question)

    print("📤 模型原始响应:\n")
    print(response.content)

    result = parser.parse(response.content)

    print("✅ JsonOutputParser 自动解析的结果:\n")
    print(result)
    print(f"姓名: {result['name']}")
    print(f"出生年份: {result['birth_year']}")
    print(f"国籍: {result['nationality']}")
    print(f"著名理论: {result['famous_theory']}")
    if "major_achievements" in result:
      achievements = result["major_achievements"]
    elif "major_ achievements" in result:
      achievements = result["major_ achievements"]
    else:
      achievements = []
    print(f"主要成就: {achievements}")
  except Exception as e:
    print(f"❌ 错误: {e}")
