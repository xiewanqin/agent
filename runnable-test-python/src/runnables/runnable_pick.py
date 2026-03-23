from langchain_core.runnables import RunnablePick, RunnableSequence

input_data = {
    "name": "小西",
    "age": 30,
    "city": "上海",
    "country": "中国",
    "email": "xiaoxi@example.com",
    "phone": "+86-19999999999",
}

chain = RunnableSequence(
    lambda input: {**input, "fullInfo": f"{input['name']}，{input['age']}岁，来自{input['city']}"},
    RunnablePick(["name", "fullInfo"]),
)

result = chain.invoke(input_data)
print(result)
