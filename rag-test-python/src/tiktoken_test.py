"""
Token 编码测试
对应 JS 版：tiktoken-test.mjs
Python 直接使用 openai 官方的 tiktoken 库
"""

import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

test_words = [
    # 英文
    "apple",
    "pineapple",
    # 中文
    "苹果",
    "吃饭",
    "一二三",
]

for word in test_words:
    tokens = enc.encode(word)
    print(f"文本: {word!r}")
    print(f"  token ids : {tokens}")
    print(f"  token 数量: {len(tokens)}")
    print()
