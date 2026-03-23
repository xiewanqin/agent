import os
from dotenv import load_dotenv
from pymilvus import MilvusClient, DataType
from langchain_community.embeddings import DashScopeEmbeddings

load_dotenv()

COLLECTION_NAME = 'weekly_report_examples'
VECTOR_DIM = 1024

EXAMPLES = [
    {
        "scenario": "支付系统稳定性治理，强调风险防控、告警收敛和应急预案完善。",
        "report_snippet": "- 本周聚焦支付链路稳定性，共处理 P1 事故 1 起、P2 事故 2 起，均在 SLA 内完成修复；\n" +
        "- 针对历史高频超时问题，完成 3 个关键接口的超时阈值和重试策略优化；\n" +
        "- 优化告警策略，合并冗余告警 10 条，新增 5 条基于 SLO 的告警规则。",
    },
    {
        "scenario": "新功能首发，更多是对外展示亮点，如新看板、新能力上线，适合发给大量跨部门同学。",
        "report_snippet": "- 上线「运营实时看板」，支持业务实时查看核心转化漏斗；\n" +
        "- 打通埋点 → DWD → 实时服务链路，为后续精细化运营提供基础；\n" +
        "- 组织 2 场跨部门分享，帮助非技术同学理解新能力的业务价值。",
    },
    {
        "scenario": "重大版本发布节奏紧凑，需要对外同步一揽子新能力，强调可视化展示和业务价值。",
        "report_snippet": "- 正式发布「增长分析 2.0」版本，新增留存分群、活动追踪等 5 项核心能力；\n" +
        "- 与市场同学联合输出发布解读文档，并在周会中向核心干系人进行路演；\n" +
        "- 配合运营梳理了 3 条重点推广场景，推动更多业务线接入新能力。",
    },
    {
        "scenario": "偏向产品体验优化和灰度试点，虽然不是大规模首发，但需要让老板看到长期产品线升级方向。",
        "report_snippet": "- 针对「自助配置」后台完成一轮体验优化，减少 3 个关键操作步骤，提升整体可用性；\n" +
        "- 在小流量场景下灰度上线「智能推荐」能力，观察首周转化率提升约 3 个百分点；\n" +
        "- 拉通产品、运营和数据同学，对后续两个月的产品升级路线图达成一致。",
    },
    {
        "scenario": "技术债清理为主，核心工作是重构、单测补齐、文档完善，节奏偏稳，不强调对外大新闻。",
        "report_snippet": "- 对老旧结算模块进行分层重构，拆出 3 个独立子模块，代码结构更加清晰；\n" +
        "- 补齐 25 条关键路径单元测试用例，整体覆盖率从 55% 提升到 68%；\n" +
        "- 完成 2 份系统设计文档补全，方便后续同学接手维护。",
    },
    {
        "scenario": "以老系统拆分和代码瘦身为主，更多是内部质量提升，重点在于风险可控和长期维护成本下降。",
        "report_snippet": "- 拆分历史「大单体」服务中的账务子模块，沉淀为独立结算服务，减少跨模块耦合；\n" +
        "- 清理 30+ 条废弃接口和配置项，并在网关层加保护，降低后续演进阻力；\n" +
        "- 对关键重构路径补充回滚预案和演练手册，保证发布过程可控。",
    },
    {
        "scenario": "聚焦测试补齐和监控完善，希望通过一轮技术债治理把「隐性风险」暴露并关掉。",
        "report_snippet": "- 新增 40+ 条端到端回归用例，覆盖主交易链路和高风险边界场景；\n" +
        "- 完成核心链路埋点和监控指标补齐，为后续 SLO 建设打下基础；\n" +
        "- 针对本周发现的 3 个潜在性能瓶颈，拉齐改造方案并排入后续技术债清单。",
    },
    {
        "scenario": "偏向团队协作和流程优化，比如值班轮值、需求评审机制、跨团队沟通等软性建设。",
        "report_snippet": "- 完成新一轮值班排班和值班手册更新，降低新同学值班心理压力；\n" +
        "- 优化需求评审流程，引入「技术风险清单」模板，帮助更早发现潜在问题；\n" +
        "- 与运维、产品同学一起梳理了故障复盘模板，后续复盘将更聚焦于可执行改进项。",
    },
]


embeddings = DashScopeEmbeddings(
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY"),
    model=os.getenv("EMBEDDINGS_MODEL_NAME", "text-embedding-v3"),
)

milvus_uri = os.getenv("MILVUS_ADDRESS", "localhost:19530")
if not milvus_uri.startswith("http"):
  milvus_uri = f"http://{milvus_uri}"

client = MilvusClient(uri=milvus_uri)


def get_embedding(text: str) -> list[float]:
  return embeddings.embed_query(text)


def ensure_collection() -> None:

  if client.has_collection(collection_name=COLLECTION_NAME):
    print(f"Dropping existing collection '{COLLECTION_NAME}'...")
    client.drop_collection(collection_name=COLLECTION_NAME)

  schema = client.create_schema(auto_id=False, enable_dynamic_field=False)
  schema.add_field(
      field_name='id',
      datatype=DataType.VARCHAR,
      max_length=100,
      is_primary=True)
  schema.add_field(field_name='vector', datatype=DataType.FLOAT_VECTOR, dim=VECTOR_DIM)
  schema.add_field(field_name='scenario', datatype=DataType.VARCHAR, max_length=2000)
  schema.add_field(
      field_name='report_snippet',
      datatype=DataType.VARCHAR,
      max_length=10000)
  client.create_collection(collection_name=COLLECTION_NAME, schema=schema)
  index_params = client.prepare_index_params()
  index_params.add_index(
      field_name='vector',
      index_type="IVF_FLAT",
      metric_type='COSINE',
      params={
          'nlist': 1024
      })
  client.create_index(collection_name=COLLECTION_NAME, index_params=index_params)
  client.load_collection(collection_name=COLLECTION_NAME)
  print('✓ 集合已加载')


def main() -> None:
  ensure_collection()

  data = []
  for i, example in enumerate(EXAMPLES):
    vector = get_embedding(example["scenario"] + example["report_snippet"])
    data.append(
        {
            "id": f"weekly_ex_{i + 1:03d}",
            **example,
            "vector": vector,
        }
    )

  client.insert(collection_name=COLLECTION_NAME, data=data)
  client.flush(collection_name=COLLECTION_NAME)
  print(f"✓ 已插入 {len(data)} 条示例")


if __name__ == "__main__":
  main()
