import os

class ModelFactory:
    """
    模型工厂：统一调度各类原生 LLM 接口，严格遵循 LangChain 社区标准包名
    """
    # 📝 手动维护的支持表 (已根据正确的 LangChain 社区包名修正)
    SUPPORTED_REASONING = [
        "openai", "ollama", "dashscope", "zhipu", "anthropic", 
        "gemini", "deepseek", "qianfan", "groq"
    ]
    SUPPORTED_EMBEDDING = [
        "openai", "ollama", "dashscope", "zhipu", "huggingface", 
        "gemini", "qianfan"
    ]

    @staticmethod
    def get_reasoning_model(provider: str, model_name: str):
        provider = provider.lower()
        
        if provider not in ModelFactory.SUPPORTED_REASONING:
            raise ValueError(f"❌ 不支持的 Reasoning Provider: '{provider}'。目前 OneBase 支持: {ModelFactory.SUPPORTED_REASONING}")

        if provider == "openai":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model=model_name, streaming=True)
            
        elif provider == "ollama":
            from langchain_community.chat_models import ChatOllama
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            return ChatOllama(model=model_name, base_url=base_url)
            
        elif provider == "dashscope":
            # 💡 修正：阿里通义千问原生接口真实类名为 ChatTongyi
            from langchain_community.chat_models import ChatTongyi
            return ChatTongyi(model=model_name, streaming=True, dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"))
            
        elif provider == "zhipu":
            # 💡 修正：智谱原生接口
            from langchain_community.chat_models import ChatZhipuAI
            return ChatZhipuAI(model=model_name, streaming=True, api_key=os.getenv("ZHIPU_API_KEY"))
            
        elif provider == "anthropic":
            # Claude 原生接口
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(model_name=model_name, streaming=True, anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"))
            
        elif provider == "gemini":
            # Google Gemini 原生接口
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(model=model_name, streaming=True, google_api_key=os.getenv("GOOGLE_API_KEY"))
            
        elif provider == "qianfan":
            # 💡 修正：百度千帆原生接口真实类名
            from langchain_community.chat_models import QianfanChatEndpoint
            return QianfanChatEndpoint(model=model_name, streaming=True, qianfan_ak=os.getenv("QIANFAN_AK"), qianfan_sk=os.getenv("QIANFAN_SK"))
            
        elif provider == "groq":
            # Groq LPU 极速推理
            from langchain_groq import ChatGroq
            return ChatGroq(model_name=model_name, groq_api_key=os.getenv("GROQ_API_KEY"), streaming=True)
            
        elif provider == "deepseek":
            # DeepSeek 官方完全拥抱 OpenAI 协议，社区最佳实践是走 ChatOpenAI 代理
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=model_name,
                openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
                openai_api_base=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
                streaming=True
            )

    @staticmethod
    def get_embedding_model(provider: str, model_name: str):
        provider = provider.lower()
        
        if provider not in ModelFactory.SUPPORTED_EMBEDDING:
            raise ValueError(f"❌ 不支持的 Embedding Provider: '{provider}'。目前 OneBase 支持: {ModelFactory.SUPPORTED_EMBEDDING}")

        if provider == "openai":
            from langchain_openai import OpenAIEmbeddings
            return OpenAIEmbeddings(model=model_name)
            
        elif provider == "ollama":
            from langchain_community.embeddings import OllamaEmbeddings
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            return OllamaEmbeddings(model=model_name, base_url=base_url)
            
        elif provider == "dashscope":
            # 阿里通义原生 Embedding
            from langchain_community.embeddings import DashScopeEmbeddings
            return DashScopeEmbeddings(model=model_name, dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"))
            
        elif provider == "zhipu":
            from langchain_community.embeddings import ZhipuAIEmbeddings
            return ZhipuAIEmbeddings(model=model_name, api_key=os.getenv("ZHIPU_API_KEY"))
            
        elif provider == "qianfan":
            from langchain_community.embeddings import QianfanEmbeddingsEndpoint
            return QianfanEmbeddingsEndpoint(model=model_name, qianfan_ak=os.getenv("QIANFAN_AK"), qianfan_sk=os.getenv("QIANFAN_SK"))
            
        elif provider == "huggingface":
            # HuggingFace 本地加载 (需要安装 sentence-transformers)
            from langchain_huggingface import HuggingFaceEmbeddings
            return HuggingFaceEmbeddings(model_name=model_name)
            
        elif provider == "gemini":
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            return GoogleGenerativeAIEmbeddings(model=model_name, google_api_key=os.getenv("GOOGLE_API_KEY"))