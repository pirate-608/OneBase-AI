from typing import List, Set
from .config import OneBaseConfig

# 模型服务商与对应 PyPI 依赖包的映射表
PROVIDER_DEPENDENCIES = {
    "openai": ["langchain-openai"],
    "ollama": ["langchain-ollama"],
    "dashscope": ["langchain-community", "dashscope"],
    "zhipu": ["langchain-community", "zhipuai"],
    "qianfan": ["langchain-community", "qianfan"],
    "modelscope": ["langchain-modelscope"],
    "google": ["langchain-google-genai"],
    "google-vertex": ["langchain-google-vertexai"],
    "deepseek": ["langchain-deepseek"], 
    "anthropic": ["langchain-anthropic"],
    "groq": ["langchain-groq"],
    "huggingface": ["langchain-huggingface", "sentence-transformers"],
    "siliconflow": ["langchain-community"],
    "doubao": ["langchain-community"]
}

def get_required_packages(config: OneBaseConfig) -> List[str]:
    """
    根据用户的配置文件，动态计算出需要额外安装的 PyPI 依赖包。
    （注：fastapi, uvicorn, langchain-core 等基建依赖默认在 onebase-ai 的安装包中）
    """
    packages: Set[str] = set()
    
    # 提取 Reasoning (推理引擎) 所需的动态依赖
    reasoning_provider = config.engine.reasoning.provider.lower()
    if reasoning_provider in PROVIDER_DEPENDENCIES:
        packages.update(PROVIDER_DEPENDENCIES[reasoning_provider])
        
    # 提取 Embedding (向量化引擎) 所需的动态依赖
    embedding_provider = config.engine.embedding.provider.lower()
    if embedding_provider in PROVIDER_DEPENDENCIES:
        packages.update(PROVIDER_DEPENDENCIES[embedding_provider])
        
    return sorted(list(packages))