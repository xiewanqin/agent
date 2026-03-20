from tiktoken import get_encoding, encoding_for_model

model_name = "gpt-4"
encoding_name = encoding_for_model(model_name)
print(encoding_name)

# 获取 tokenizer，用来把文本转成 token，从而精确控制 LLM 上下文大小
enc = get_encoding("cl100k_base")
print('apple', len(enc.encode("apple")))  # 编码成token
print('pineapple', len(enc.encode("pineapple")))
print('苹果', len(enc.encode("苹果")))
print('吃饭', len(enc.encode("吃饭")))
print('一二三', len(enc.encode("一二三")))
