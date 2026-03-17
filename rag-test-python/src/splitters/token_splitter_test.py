"""
Token 分割器测试
对应 JS 版：TokenTextSplitter-test.mjs
"""

import tiktoken
from langchain_core.documents import Document
from langchain_text_splitters import TokenTextSplitter

log_document = Document(
    page_content="""[2024-01-15 10:00:00] INFO: Application started
[2024-01-15 10:00:05] DEBUG: Loading configuration file
[2024-01-15 10:00:10] INFO: Database connection established
[2024-01-15 10:00:15] WARNING: Rate limit approaching
[2024-01-15 10:00:20] ERROR: Failed to process request
[2024-01-15 10:00:25] INFO: Retrying operation
[2024-01-15 10:00:30] SUCCESS: Operation completed"""
)

text_splitter = TokenTextSplitter(
    chunk_size=50,      # 每个块最多 50 个 Token
    chunk_overlap=10,   # 块之间重叠 10 个 Token
    encoding_name="cl100k_base",
)

split_documents = text_splitter.split_documents([log_document])

enc = tiktoken.get_encoding("cl100k_base")

for doc in split_documents:
    print(doc)
    print("character length:", len(doc.page_content))
    print("token length:", len(enc.encode(doc.page_content)))
    print()
