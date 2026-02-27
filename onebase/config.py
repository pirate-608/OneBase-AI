import yaml
from pathlib import Path
from typing import Dict, Any, List, Union  # 🌟 新增 Union
from pydantic import BaseModel, Field, ValidationError

# --- 1. 定义数据模型 ---

class ModelProvider(BaseModel):
    provider: str
    model: str

class EngineConfig(BaseModel):
    reasoning: ModelProvider
    embedding: ModelProvider

class DatabaseConfig(BaseModel):
    type: str = "postgresql"
    vector_store: str = "pgvector"

class KnowledgeBaseConfig(BaseModel):
    path: str = "./base"
    chunk_size: int = Field(default=500, gt=0, description="文本切块大小必须大于0")
    # 🌟 修改点：struct 允许是字典、字符串（如 "default"），或者不填（默认为 "default"）
    struct: Union[Dict[str, Any], str, None] = Field(default="default")

class OneBaseConfig(BaseModel):
    site_name: str
    engine: EngineConfig
    database: DatabaseConfig
    knowledge_base: KnowledgeBaseConfig
    # 兼容列表中包含字典的写法，例如: - chat_history: true
    features: List[Dict[str, bool]]

    # --- 2. 核心加载与校验方法 ---
    @classmethod
    def load(cls, yaml_path: str | Path) -> "OneBaseConfig":
        path = Path(yaml_path)
        if not path.exists():
            raise FileNotFoundError(f"找不到配置文件: {path}")

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Pydantic 魔法在这里发生：将字典解包注入，自动校验所有字段
            return cls(**data)
            
        except yaml.YAMLError as e:
            raise ValueError(f"YAML 格式错误，请检查缩进和语法:\n{e}")
        # ValidationError 我们会在 CLI 层捕获，以便更优雅地打印