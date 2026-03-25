import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
load_dotenv()

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)


class TranslationOutput(BaseModel):
  translation: str = Field(description="翻译后的英文文本")
  keywords: list[str] = Field(description="3个关键词", min_length=3, max_length=3)


output_parser = PydanticOutputParser(pydantic_object=TranslationOutput)

prompt_template = PromptTemplate.from_template(
    "将以下文本翻译成英文，然后总结为3个关键词。\n\n文本：{text}\n\n{format_instructions}"
)

variables = {
    "text": "LangChain 是一个强大的 AI 应用开发框架",
    "format_instructions": output_parser.get_format_instructions(),
}

formatted_prompt = prompt_template.format(**variables)
print("\n===== 发送给模型的消息 =====\n")
print(formatted_prompt)
response = model.invoke(formatted_prompt)

print("\n===== 模型输出 =====\n")
print(response.content)

# 解析输出
result = output_parser.parse(response.content)
print("\n===== 解析输出 =====\n")
print(result)
