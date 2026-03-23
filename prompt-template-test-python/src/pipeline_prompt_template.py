"""
对应 prompt-template-test/src/pipeline-prompt-template.mjs

langchain_core 新版本已移除 PipelinePromptTemplate，此处用等价实现：
先分别 format 各子模板，再把结果填入 final_prompt 的占位符。
"""
from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

load_dotenv()


class PipelinePromptTemplate:
    """与旧版 LangChain 行为一致：多段 PromptTemplate 组合成最终字符串。"""

    def __init__(
        self,
        *,
        pipeline_prompts: list[dict[str, Any]],
        final_prompt: PromptTemplate,
        partial_kwargs: dict[str, Any] | None = None,
    ) -> None:
        self.pipeline_prompts = pipeline_prompts
        self.final_prompt = final_prompt
        self.partial_kwargs: dict[str, Any] = dict(partial_kwargs or {})

    def partial(self, **kwargs: Any) -> PipelinePromptTemplate:
        """预先绑定部分变量（与 JS 版 pipelinePrompt.partial 一致），返回新实例。"""
        merged = {**self.partial_kwargs, **kwargs}
        return PipelinePromptTemplate(
            pipeline_prompts=self.pipeline_prompts,
            final_prompt=self.final_prompt,
            partial_kwargs=merged,
        )

    def format(self, **kwargs: Any) -> str:
        full = {**self.partial_kwargs, **kwargs}
        blocks: dict[str, str] = {}
        for item in self.pipeline_prompts:
            name = item["name"]
            prompt: PromptTemplate = item["prompt"]
            sub = {k: full[k] for k in prompt.input_variables}
            blocks[name] = prompt.format(**sub)
        return self.final_prompt.format(**blocks)

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)

# A. 人设模块（导出以便在其他场景复用）
persona_prompt = PromptTemplate.from_template(
    "你是一名资深工程团队负责人，写作风格：{tone}。\n"
    "你擅长把枯燥的技术细节写得既专业又有温度。\n"
)

# B. 背景模块（导出以便在其他场景复用）
context_prompt = PromptTemplate.from_template(
    "公司：{company_name}\n"
    "部门：{team_name}\n"
    "直接汇报对象：{manager_name}\n"
    "本周时间范围：{week_range}\n"
    "本周部门核心目标：{team_goal}\n"
)

# C. 任务模块
task_prompt = PromptTemplate.from_template(
    "以下是本周团队的开发活动（Git / Jira 汇总）：\n"
    "{dev_activities}\n"
    "请你从这些原始数据中提炼出：\n"
    "1. 本周整体成就亮点\n"
    "2. 潜在风险和技术债\n"
    "3. 下周重点计划建议\n"
)

# D. 格式模块
format_prompt = PromptTemplate.from_template(
    "请用 Markdown 输出周报，结构包含：\n"
    "1. 本周概览（2-3 句话的 Summary）\n"
    "2. 详细拆分（按模块或项目分段）\n"
    "3. 关键指标表格，表头为：模块 | 亮点 | 风险 | 下周计划\n"
    "注意：\n"
    "- 尽量引用一些具体数据（如提交次数、完成的任务编号）\n"
    "- 语气专业，但可以偶尔带一点轻松的口吻，符合 {company_values}。\n"
)

# E. 最终组合 Prompt（把上面几个模块拼在一起）
final_prompt = PromptTemplate.from_template(
    "{persona_block}\n"
    "{context_block}\n"
    "{task_block}\n"
    "{format_block}\n"
    "现在请生成本周的最终周报："
)

pipeline_prompt = PipelinePromptTemplate(
    pipeline_prompts=[
        {"name": "persona_block", "prompt": persona_prompt},
        {"name": "context_block", "prompt": context_prompt},
        {"name": "task_block", "prompt": task_prompt},
        {"name": "format_block", "prompt": format_prompt},
    ],
    final_prompt=final_prompt
)

if __name__ == "__main__":
    pipeline_formatted = pipeline_prompt.format(
        tone="专业、清晰、略带幽默",
        company_name="星航科技",
        team_name="数据智能平台组",
        manager_name="张三",
        week_range="2026-03-22 ~ 2026-03-28",
        team_goal="完成数据智能平台组的工作",
        dev_activities="""
    - Git: 58 次提交，3 个主要分支合并
    - Jira: 完成 12 个 Story，关闭 7 个 Bug
    - 关键任务：完成智能周报 Pipeline 设计、实现 Prompt 拆分、接入 ExampleSelector
    """,
        company_values="「极致、开放、靠谱」的价值观",
    )

    print("PipelinePromptTemplate 组合后的 Prompt：")
    print(pipeline_formatted)
