import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)

prompt = "详细介绍莫扎特的信息。"

stream = model.stream(prompt)

full_content = ""
chunk_count = 0

try:
  for chunk in stream:
    if chunk.content:  # 防止 None
      chunk_count += 1
      full_content += chunk.content
      print(chunk.content, end="", flush=True)

except Exception as e:
  print("\n流式输出异常:", e)

finally:
  print("\n\n=== 统计信息 ===")
  print(f"共接收 {chunk_count} 个数据块")
  print(f"完整内容长度: {len(full_content)}")
