import os
from typing import List
from langchain_core.documents import Document
from langchain_postgres.vectorstores import PGVector
from .factory import ModelFactory


class VectorStoreManager:
    def __init__(self, config):
        self.config = config

        # 🌟 [3-1] 数据库凭据从 .env 环境变量读取，不再硬编码
        from dotenv import load_dotenv

        load_dotenv()  # 加载项目根目录的 .env 文件

        db_user = os.getenv("POSTGRES_USER", "onebase")
        db_pass = os.getenv("POSTGRES_PASSWORD", "onebase_secret")
        db_name = os.getenv("POSTGRES_DB", "onebase_db")
        # 注意：这里假设我们在宿主机运行 CLI，所以连接 localhost
        self.connection_string = (
            f"postgresql+psycopg://{db_user}:{db_pass}@localhost:5432/{db_name}"
        )

        # 2. 集合名称（可用来区分不同的项目或知识库版本）
        self.collection_name = self.config.site_name.replace(" ", "_").lower()

        # 3. 根据配置动态生成向量模型实例
        self.embeddings = ModelFactory.get_embedding_model(
            provider=self.config.engine.embedding.provider,
            model_name=self.config.engine.embedding.model,
        )

    def ingest(self, chunks: List[Document]):
        """将切片转换为向量并存入 pgvector"""

        # 2. 初始化 PGVector 连接
        # PGVector 会自动在数据库中创建表结构（如果不存在的话）
        vector_store = PGVector(
            embeddings=self.embeddings,
            collection_name=self.collection_name,
            connection=self.connection_string,
            use_jsonb=True,  # 开启 JSONB 存储 metadata，对结构化检索更友好
        )

        # 3. 执行入库（内部会调用模型 API 获取向量，并执行 SQL 插入）
        # 这里可以加入批处理逻辑，防止一次性发送太多请求导致 API 触发 Rate Limit
        batch_size = 100
        total_chunks = len(chunks)

        for i in range(0, total_chunks, batch_size):
            batch = chunks[i : i + batch_size]
            vector_store.add_documents(batch)

        return total_chunks
