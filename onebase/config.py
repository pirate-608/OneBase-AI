import yaml
from pathlib import Path
from typing import Dict, Any, Literal, Union
from pydantic import BaseModel, Field, ValidationError

# --- 1. 定义数据模型 ---


class ModelProvider(BaseModel):
    provider: str
    model: str


class EngineConfig(BaseModel):
    reasoning: ModelProvider
    embedding: ModelProvider


class DatabaseConfig(BaseModel):
    type: Literal["postgresql"] = "postgresql"
    vector_store: Literal["pgvector"] = "pgvector"


class KnowledgeBaseConfig(BaseModel):
    path: str = "./base"
    chunk_size: int = Field(default=500, gt=0, description="文本切块大小必须大于0")
    struct: Union[Dict[str, Any], str, None] = Field(default="default")


# 🌟 [Step1] 强类型 Feature Flags 配置
class FeaturesConfig(BaseModel):
    chat_history: bool = True
    file_upload: bool = True


class PerformanceConfig(BaseModel):
    redis_cache_enabled: bool = True
    redis_context_cache_ttl_seconds: int = Field(default=300, gt=0)
    rate_limit_enabled: bool = True
    chat_rate_limit_per_minute: int = Field(default=30, gt=0)
    upload_rate_limit_per_minute: int = Field(default=6, gt=0)


class OneBaseConfig(BaseModel):
    site_name: str
    engine: EngineConfig
    database: DatabaseConfig
    knowledge_base: KnowledgeBaseConfig
    features: FeaturesConfig = FeaturesConfig()
    performance: PerformanceConfig = PerformanceConfig()

    # --- 2. 核心加载与校验方法 ---
    @classmethod
    def load(cls, yaml_path: str | Path) -> "OneBaseConfig":
        path = Path(yaml_path)
        if not path.exists():
            raise FileNotFoundError(f"找不到配置文件: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # Pydantic 魔法在这里发生：将字典解包注入，自动校验所有字段
            return cls(**data)

        except yaml.YAMLError as e:
            raise ValueError(f"YAML 格式错误，请检查缩进和语法:\n{e}")
        # ValidationError 我们会在 CLI 层捕获，以便更优雅地打印
