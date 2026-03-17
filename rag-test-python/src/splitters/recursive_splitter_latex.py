"""
LaTeX 文本分割器测试
对应 JS 版：recursive-splitter-latex.mjs
"""

from langchain_core.documents import Document
from langchain_text_splitters import LatexTextSplitter

latex_text = r"""\int x^{\mu}\mathrm{d}x=\frac{x^{\mu +1}}{\mu +1}+C, \left({\mu \neq -1}\right) \int \frac{1}{\sqrt{1-x^{2}}}\mathrm{d}x= \arcsin x +C \int \frac{1}{\sqrt{1-x^{2}}}\mathrm{d}x= \arcsin x +C \begin{pmatrix}  
  a_{11} & a_{12} & a_{13} \\  
  a_{21} & a_{22} & a_{23} \\  
  a_{31} & a_{32} & a_{33}  
\end{pmatrix} """

latex_doc = Document(page_content=latex_text)

latex_splitter = LatexTextSplitter(
    chunk_size=200,
    chunk_overlap=40,
)

split_documents = latex_splitter.split_documents([latex_doc])

for doc in split_documents:
    print(doc)
    print("character length:", len(doc.page_content))
    print()
