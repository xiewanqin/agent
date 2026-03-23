"""
对应 prompt-template-test/src/example-selector2.mjs

使用 SemanticSimilarityExampleSelector + Milvus 已有集合做 few-shot 示例选取。

说明：Python 里没有 JS 的 Milvus.fromExistingCollection，应使用
langchain_community.vectorstores.Milvus；集合已存在且已有索引时，传 drop_old=False，
index_params / search_params 与写入脚本一致即可（若已有索引则不会重复创建）。

SemanticSimilarityExampleSelector 只从 Document.metadata 取示例字段；Milvus 会把
text_field 放进 page_content，其余标量进 metadata。故用 primary 键列作 text_field，
让 scenario、report_snippet 都留在 metadata，并用 example_keys 过滤掉 id。
"""
import os

from dotenv import load_dotenv
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import Milvus
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()

COLLECTION_NAME = os.getenv("MILVUS_COLLECTION_NAME", "weekly_report_examples")

embeddings = DashScopeEmbeddings(
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY"),
    model=os.getenv("EMBEDDINGS_MODEL_NAME", "text-embedding-v3"),
)

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)

example_prompt = PromptTemplate.from_template(
    """用户场景：{scenario}
生成的周报片段：
{report_snippet}
---"""
)

milvus_address = os.getenv("MILVUS_ADDRESS", "localhost:19530")

# 等价于 JS：Milvus.fromExistingCollection(embeddings, { collectionName, clientConfig, indexCreateOptions })
vector_store = Milvus(
    embedding_function=embeddings,
    collection_name=COLLECTION_NAME,
    connection_args={"address": milvus_address},
    drop_old=False,
    auto_id=False,
    primary_field="id",
    text_field="id",
    vector_field="vector",
    index_params={
        "index_type": "IVF_FLAT",
        "metric_type": "COSINE",
        "params": {"nlist": 1024},
    },
    search_params={"metric_type": "COSINE", "params": {"nprobe": 10}},
)

example_selector = SemanticSimilarityExampleSelector(
    vectorstore=vector_store,
    k=2,
    input_keys=["current_scenario"],
    example_keys=["scenario", "report_snippet"],
)

few_shot_prompt = FewShotPromptTemplate(
    example_prompt=example_prompt,
    example_selector=example_selector,
    prefix=(
        "下面是一些不同类型的周报示例，你可以从中学习语气和结构"
        "（系统会自动从 Milvus 选出和当前场景最相近的示例）：\n"
    ),
    suffix=(
        "\n\n现在请根据上面的示例风格，为下面这个场景写一份新的周报：\n"
        "场景描述：{current_scenario}\n"
        "请输出一份适合发给老板和团队同步的 Markdown 周报草稿。"
    ),
    input_variables=["current_scenario"],
)


def main() -> None:
    current_scenario_1 = (
        "我们本周主要是在清理历史技术债：重构老旧的订单模块、补齐核心接口的单测，"
        "同时也完善了一些文档，方便后面新人接手。整体没有对外大范围发布的新功能。"
    )
    current_scenario_2 = (
        "本周完成新一代运营看板的首批功能上线，重点打通埋点和实时数仓链路，"
        "并面向运营和市场同学做了多场宣讲，希望更多同学开始使用新能力。"
    )

    print("\n===== 场景 1：技术债清理为主 =====\n")
    print(few_shot_prompt.format(current_scenario=current_scenario_1))

    print("\n\n===== 场景 2：新功能首发 + 对外宣传 =====\n")
    print(few_shot_prompt.format(current_scenario=current_scenario_2))

    # 需要真调模型时解开：
    out = model.invoke(few_shot_prompt.format(current_scenario=current_scenario_1))
    print(out.content)


if __name__ == "__main__":
    main()
