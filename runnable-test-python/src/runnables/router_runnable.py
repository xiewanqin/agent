from langchain_core.runnables import RouterRunnable, RunnableLambda

router = RouterRunnable(
    runnables={
        "toUpperCase": RunnableLambda(lambda text: text.upper()),
        "reverseText": RunnableLambda(lambda text: text[::-1]),
    }
)

result = router.invoke({"key": "toUpperCase", "input": "Hello World"})
print(f"toUpperCase 结果: {result}")

result = router.invoke({"key": "reverseText", "input": "Hello World"})
print(f"reverseText 结果: {result}")
