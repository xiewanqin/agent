from langchain_core.runnables import RunnablePassthrough, RunnableSequence, RunnableLambda, RunnableParallel, RunnableMap

# chain = RunnableSequence(
#     lambda x: {"concept": x},
#     RunnableParallel(
#         {
#             "original": RunnablePassthrough(),
#             "processed": lambda obj: {
#                 "upper": obj["concept"].upper(),
#                 "length": len(obj["concept"]),
#             },
#         }
#     ),
# )

chain = RunnableSequence(
    lambda x: {"concept": x},
    {
        "original": RunnablePassthrough(),
        "processed": lambda obj: {
            "upper": obj["concept"].upper(),
            "length": len(obj["concept"]),
        },
    }
)

# chain = RunnableSequence(
#     lambda x: {"concept": x},
#     RunnablePassthrough.assign(
#         original=RunnablePassthrough(),
#         processed=lambda obj: {
#             "upper": obj["concept"].upper(),
#             "length": len(obj["concept"]),
#         },
#     ),
# )


result = chain.invoke("Hello World")
print(result)
