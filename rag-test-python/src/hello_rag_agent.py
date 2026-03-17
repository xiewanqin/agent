"""
hello_rag_agent.py - Agent 版 RAG

Dashscope qwen-plus 不支持 tool_choice 强制调用工具，
改为：第一轮手动执行检索并注入 ToolMessage，模拟 agent 已调用工具，
后续由模型基于检索结果生成回答。输出效果与 create_agent 一致。
"""

import asyncio
import os

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    temperature=0,
)

embeddings = OpenAIEmbeddings(
    api_key=os.getenv("OPENAI_API_KEY"),
    model=os.getenv("EMBEDDINGS_MODEL_NAME"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    check_embedding_ctx_length=False,
)

documents = [
    Document(
        page_content="光光是一个活泼开朗的小男孩，他有一双明亮的大眼睛，总是带着灿烂的笑容。光光最喜欢的事情就是和朋友们一起玩耍，他特别擅长踢足球，每次在球场上奔跑时，就像一道阳光一样充满活力。",
        metadata={"chapter": 1, "character": "光光", "type": "角色介绍", "mood": "活泼"},
    ),
    Document(
        page_content="东东是光光最好的朋友，他是一个安静而聪明的男孩。东东喜欢读书和画画，他的画总是充满了想象力。虽然性格不同，但东东和光光从幼儿园就认识了，他们一起度过了无数个快乐的时光。",
        metadata={"chapter": 2, "character": "东东", "type": "角色介绍", "mood": "温馨"},
    ),
    Document(
        page_content="有一天，学校要举办一场足球比赛，光光非常兴奋，他邀请东东一起参加。但是东东从来没有踢过足球，他担心自己会拖累光光。光光看出了东东的担忧，他拍着东东的肩膀说：\u201c没关系，我们一起练习，我相信你一定能行的！\u201d",
        metadata={"chapter": 3, "character": "光光和东东", "type": "友情情节", "mood": "鼓励"},
    ),
    Document(
        page_content="接下来的日子里，光光每天放学后都会教东东踢足球。光光耐心地教东东如何控球、传球和射门，而东东虽然一开始总是踢不好，但他从不放弃。东东也用自己的方式回报光光，他画了一幅画送给光光，画上是两个小男孩在球场上一起踢球的场景。",
        metadata={"chapter": 4, "character": "光光和东东", "type": "友情情节", "mood": "互助"},
    ),
    Document(
        page_content="比赛那天终于到了，光光和东东一起站在球场上。虽然东东的技术还不够熟练，但他非常努力，而且他用自己的观察力帮助光光找到了对手的弱点。在关键时刻，东东传出了一个漂亮的球，光光接球后射门得分！他们赢得了比赛，更重要的是，他们的友谊变得更加深厚了。",
        metadata={"chapter": 5, "character": "光光和东东", "type": "高潮转折", "mood": "激动"},
    ),
    Document(
        page_content="从那以后，光光和东东成为了学校里最要好的朋友。光光教东东运动，东东教光光画画，他们互相学习，共同成长。每当有人问起他们的友谊，他们总是笑着说：\u201c真正的朋友就是互相帮助，一起变得更好的人！\u201d",
        metadata={"chapter": 6, "character": "光光和东东", "type": "结局", "mood": "欢乐"},
    ),
    Document(
        page_content="多年后，光光成为了一名职业足球运动员，而东东成为了一名优秀的插画师。虽然他们走上了不同的道路，但他们的友谊从未改变。东东为光光设计了球衣上的图案，光光在每场比赛后都会给东东打电话分享喜悦。他们证明了，真正的友情可以跨越时间和距离，永远闪闪发光。",
        metadata={"chapter": 7, "character": "光光和东东", "type": "尾声", "mood": "温馨"},
    ),
]

SYSTEM_PROMPT = SystemMessage(content=(
    "你是一个讲友情故事的老师，只能基于 search_story 工具检索到的内容来回答问题，"
    "不能编造故事内容。如果检索结果中没有相关细节，就说'这个故事里还没有提到这个细节'。"
))


async def main():
    print("正在创建向量存储...")
    vector_store = await InMemoryVectorStore.afrom_documents(documents, embeddings)
    print("向量存储创建完成\n")

    @tool
    async def search_story(query: str) -> str:
        """根据问题从故事中检索最相关的片段，用于回答关于光光和东东故事的问题"""
        scored_results = await vector_store.asimilarity_search_with_score(query, k=3)

        print("\n【检索到的文档及相似度评分】")
        result_parts = []
        for i, (doc, score) in enumerate(scored_results):
            print(f"\n[文档 {i + 1}] 相似度: {score:.4f}")
            print(f"内容: {doc.page_content}")
            m = doc.metadata
            print(f"元数据: 章节={m['chapter']}, 角色={m['character']}, 类型={m['type']}, 心情={m['mood']}")
            result_parts.append(f"[片段{i + 1}]\n{doc.page_content}")

        return "\n\n━━━━━\n\n".join(result_parts)

    model_with_tools = model.bind_tools([search_story])

    questions = ["东东和光光是怎么成为朋友的？"]

    for question in questions:
        print("=" * 80)
        print(f"问题: {question}")
        print("=" * 80)

        # Dashscope 不支持 tool_choice，手动执行检索并注入消息，模拟 agent 调用
        print(f"\n🤖 AI 决定调用: [search_story]  参数: query={question}")
        search_result = await search_story.ainvoke({"query": question})
        preview = str(search_result)[:120].replace("\n", " ")
        print(f"🔧 [search_story] 返回: {preview}{'...' if len(str(search_result)) > 120 else ''}")

        # 构造 AIMessage + ToolMessage，让模型基于检索结果回答
        fake_tool_call_id = "call_manual_rag"
        messages = [
            SYSTEM_PROMPT,
            HumanMessage(content=question),
            AIMessage(content="", tool_calls=[{"id": fake_tool_call_id, "name": "search_story", "args": {"query": question}}]),
            ToolMessage(content=str(search_result), tool_call_id=fake_tool_call_id),
        ]

        response = await model_with_tools.ainvoke(messages)
        print(f"\n✨ AI 最终回复:\n{response.content}\n")


if __name__ == "__main__":
    asyncio.run(main())
