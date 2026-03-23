import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

load_dotenv()

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)

naive_prompt = PromptTemplate.from_template(
    "你是一名严谨但不失人情味的工程团队负责人，需要根据本周数据写一份周报。\n\n"
    "公司名称：{company_name}\n"
    "部门名称：{team_name}\n"
    "直接汇报对象：{manager_name}\n"
    "本周时间范围：{week_range}\n\n"
    "本周团队核心目标：{team_goal}\n\n"
    "本周开发数据（Git 提交 / Jira 任务）：{dev_activities}\n\n"
    "请根据以上信息生成一份【Markdown 周报】，要求：\n"
    "- 有简短的整体 summary（两三句话）\n"
    "- 有按模块/项目拆分的小结\n"
    "- 用一个 Markdown 表格列出关键指标（字段示例：模块 / 亮点 / 风险 / 下周计划）\n"
    "- 语气专业但有一点人情味，适合作为给老板和团队抄送的周报。"
)

promt = naive_prompt.format(
    company_name="星航科技",
    team_name="数据智能平台组",
    manager_name="张三",
    week_range="2026-03-22 ~ 2026-03-28",
    team_goal="完成数据智能平台组的工作",
    dev_activities="完成数据智能平台组的工作"
)

print("格式化后的提示词:")
print(promt)


# response = model.invoke(promt)
# print(response.content)

# stream = model.stream(promt)

# print("流式输出: AI 回答")
# for chunk in stream:
#   print(chunk.content, end="", flush=True)

# print("\n流式输出: 完成")


# 链式写法

print("链式流式输出: 开始")

chain = naive_prompt | model

for chunk in chain.stream({
    "company_name": "星航科技",
    "team_name": "数据智能平台组",
    "manager_name": "张三",
    "week_range": "2026-03-22 ~ 2026-03-28",
    "team_goal": "完成数据智能平台组的工作",
    "dev_activities": "完成数据智能平台组的工作"
}):
  print(chunk.content, end="", flush=True)

print("\n链式流式输出: 完成")
