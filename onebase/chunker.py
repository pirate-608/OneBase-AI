from pathlib import Path
from typing import List, Dict
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class DocumentProcessor:
    def __init__(self, chunk_size: int, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        # RecursiveCharacterTextSplitter 是目前最推荐的切词器
        # 它会尽量保持段落和句子的完整性
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

    def process(self, valid_docs: List[Dict]) -> List[Document]:
        """
        接收 builder.py 传来的文件列表，读取并切片
        """
        all_chunks = []

        for doc_info in valid_docs:
            file_path: Path = doc_info["file_path"]
            ext = file_path.suffix.lower()

            # 1. 根据后缀选择合适的 Loader
            try:
                if ext in [".txt", ".md"]:
                    # 文本类型直接读取
                    loader = TextLoader(str(file_path), encoding="utf-8")
                elif ext == ".pdf":
                    # PDF 类型使用 PyPDFLoader
                    loader = PyPDFLoader(str(file_path))
                else:
                    # 暂不支持的格式跳过
                    continue
                
                # 加载整篇文档
                loaded_docs = loader.load()

            except Exception as e:
                print(f"警告: 读取文件 {file_path} 失败: {e}")
                continue

            # 2. 注入我们从 YAML 中解析出的「灵魂」元数据
            for doc in loaded_docs:
                doc.metadata["title"] = doc_info["title"]
                # 将面包屑列表拼接成字符串，方便后续数据库存储和检索
                doc.metadata["breadcrumbs"] = " > ".join(doc_info["breadcrumbs"])
                doc.metadata["source_file"] = file_path.name

            # 3. 执行切片
            chunks = self.text_splitter.split_documents(loaded_docs)
            all_chunks.extend(chunks)

        return all_chunks