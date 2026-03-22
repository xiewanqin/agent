import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)

prompt = "请介绍一下爱因斯坦的信息。请以 JSON 格式返回，包含以下字段：name（姓名）、birth_year（出生年份）、nationality（国籍）、major_achievements（主要成就，数组）、famous_theory（著名理论）。"

response = model.invoke(prompt)

print("✅ 收到响应:")
print(response.content)

json_result = json.loads(response.content)
print("📋 解析后的 JSON 对象:")
print(json_result)

print(f"姓名: {json_result['name']}")
print(f"出生年份: {json_result['birth_year']}")
print(f"国籍: {json_result['nationality']}")
print(f"著名理论: {json_result['famous_theory']}")
print(f"主要成就: {json_result['major_achievements']}")
