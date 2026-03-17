"""
网页加载 + 文本分割
对应 JS 版：loader-and-splitter.mjs
使用 WebBaseLoader（BeautifulSoup）替代 CheerioWebBaseLoader
"""

import os

import bs4
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

loader = WebBaseLoader(
    web_paths=["https://juejin.cn/post/7233327509919547452"],
    # 对应 JS 的 selector: '.main-area p'，抓取 .main-area 内的段落内容
    # bs_kwargs={"parse_only": bs4.SoupStrainer(class_="main-area")},
)

# documents = loader.load()
raw_docs = loader.load()

# 对应 JS 的 selector: '.main-area p'，手动提取 .main-area 内所有段落文本
soup = bs4.BeautifulSoup(raw_docs[0].page_content, "html.parser")
main_area = soup.find(class_="main-area")
text = "\n".join(p.get_text() for p in main_area.find_all("p")
                 ) if main_area else raw_docs[0].page_content
documents = [Document(page_content=text, metadata=raw_docs[0].metadata)]

print(f"总字符数: {len(documents[0].page_content)}")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=50,
    separators=["。", "！", "？"],
)

split_documents = text_splitter.split_documents(documents)

for doc in split_documents:
  print(doc)
  print()

print(f"\n文档分割完成，共 {len(split_documents)} 个分块")
