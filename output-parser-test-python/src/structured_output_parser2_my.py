"""
与 structured_output_parser2.py 相同逻辑，便于对照练习。
对应 output-parser-test/src/structured-output-parser2.mjs
"""

import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

load_dotenv()

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)


class Award(BaseModel):
  name: str = Field(description="奖项名称")
  year: int = Field(description="获奖年份")
  reason: str | None = Field(default=None, description="获奖原因")


class FamousTheory(BaseModel):
  name: str = Field(description="理论名称")
  year: int | None = Field(default=None, description="提出年份")
  description: str = Field(description="理论简要描述")


class Education(BaseModel):
  university: str = Field(description="主要毕业院校")
  degree: str = Field(description="学位")
  graduation_year: int | None = Field(default=None, description="毕业年份")


class Scientist(BaseModel):
  """与 zod scientistSchema 对应"""

  name: str = Field(description="科学家的全名")
  birth_year: int = Field(description="出生年份")
  death_year: int | None = Field(default=None, description="去世年份，如果还在世则不填")
  nationality: str = Field(description="国籍")
  fields: list[str] = Field(description="研究领域列表")
  awards: list[Award] = Field(description="获得的重要奖项列表")
  major_achievements: list[str] = Field(description="主要成就列表")
  famous_theories: list[FamousTheory] = Field(description="著名理论列表")
  education: Education | None = Field(default=None, description="教育背景")
  biography: str = Field(description="简短传记，100字以内")


parser = PydanticOutputParser(pydantic_object=Scientist)

question = f"""请介绍一下居里夫人（Marie Curie）的详细信息，包括她的教育背景、研究领域、获得的奖项、主要成就和著名理论。

{parser.get_format_instructions()}"""

print("📋 生成的提示词:\n")
print(question)

try:
  print("🤔 正在调用大模型（使用 Pydantic Schema）...\n")

  response = model.invoke(question)

  print("📤 模型原始响应:\n")
  print(response.content)

  result = parser.parse(response.content)

  print("✅ PydanticOutputParser 自动解析并验证的结果:\n")
  print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))

  print("📊 格式化展示:\n")
  print(f"👤 姓名: {result.name}")
  print(f"📅 出生年份: {result.birth_year}")
  if result.death_year is not None:
    print(f"⚰️  去世年份: {result.death_year}")
  print(f"🌍 国籍: {result.nationality}")
  print(f"🔬 研究领域: {', '.join(result.fields)}")

  print("\n🎓 教育背景:")
  if result.education:
    print(f"   院校: {result.education.university}")
    print(f"   学位: {result.education.degree}")
    if result.education.graduation_year is not None:
      print(f"   毕业年份: {result.education.graduation_year}")

  print(f"\n🏆 获得的奖项 ({len(result.awards)}个):")
  for index, award in enumerate(result.awards):
    print(f"   {index + 1}. {award.name} ({award.year})")
    if award.reason:
      print(f"      原因: {award.reason}")

  print(f"\n💡 著名理论 ({len(result.famous_theories)}个):")
  for index, theory in enumerate(result.famous_theories):
    print(f"   {index + 1}. {theory.name} ({theory.year})")
    print(f"      {theory.description}")

  print(f"\n🌟 主要成就 ({len(result.major_achievements)}个):")
  for index, achievement in enumerate(result.major_achievements):
    print(f"   {index + 1}. {achievement}")

  print("\n📖 传记:")
  print(f"   {result.biography}")

except Exception as e:
  print(f"❌ 错误: {e}")
  # Pydantic 校验失败时会有 ValidationError
  from pydantic import ValidationError

  if isinstance(e, ValidationError):
    print("验证错误详情:", e.errors())
