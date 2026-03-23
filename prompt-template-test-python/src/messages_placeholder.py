import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import convert_to_openai_messages, message_to_dict

load_dotenv()

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)

chat_prompt_with_history = ChatPromptTemplate.from_messages([
    ("system", "你是一名资深工程效率顾问，善于在多轮对话的上下文中给出具体、可执行的建议。"),
    MessagesPlaceholder("history"),
    ("human", """这是用户本轮的新问题：{current_input}
    请结合上面的历史对话，一并给出你的建议。
    """),
])

history_messages = [
    ("human", "我们团队最近在做一个内部的周报自动生成工具。"),
    ("ai", "听起来不错，可以先把数据源（Git / Jira / 运维）梳理清楚，再考虑 Prompt 模块化设计。"),
    ("human", "我们已经把 Prompt 拆成了「人设」「背景」「任务」「格式」四块。"),
    ("ai", "很好，接下来可以考虑把这些模块做成可复用的 PipelinePromptTemplate，方便在不同场景复用。"),
]


formatted_messages = chat_prompt_with_history.format_messages(
    history=history_messages,
    current_input="现在我们想再优化一下多人协同编辑周报的流程，有什么建议？",
)

print("包含历史对话的消息数组（OpenAI role/content 风格 JSON）：")
print(
    json.dumps(
        convert_to_openai_messages(formatted_messages),
        indent=2,
        ensure_ascii=False,
    )
)

print("包含历史对话的消息数组（LangChain 原生消息对象）,LangChain 自带的完整结构（含 additional_kwargs 等）：")
print(
    json.dumps(
        [message_to_dict(m) for m in formatted_messages],
        indent=2,
        ensure_ascii=False,
    )
)

response = model.invoke(formatted_messages)

print("\nAI 回复内容：")
print(response.content)
