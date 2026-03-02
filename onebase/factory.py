import os
import re


def _docker_rewrite(url: str | None) -> str | None:
    """容器内运行时，自动将 localhost / 127.0.0.1 替换为 host.docker.internal"""
    if url and os.getenv("RUNNING_IN_DOCKER"):
        return re.sub(r"localhost|127\.0\.0\.1", "host.docker.internal", url)
    return url


def _get_openai_base_url() -> str | None:
    """兼容两种环境变量名：OPENAI_BASE_URL（官方惯例）和 OPENAI_API_BASE（旧版）"""
    return _docker_rewrite(os.getenv("OPENAI_BASE_URL") or os.getenv("OPENAI_API_BASE"))


class ModelFactory:
    """
    模型工厂：统一调度各类原生 LLM 接口，严格遵循 LangChain 社区标准包名
    """

    # 📝 手动维护的支持表 (已根据正确的 LangChain 社区包名修正)
    SUPPORTED_REASONING = [
        "openai",
        "ollama",
        "dashscope",
        "zhipu",
        "anthropic",
        "google",
        "deepseek",
        "qianfan",
        "groq",
        "modelscope",
        "google-vertex",
        "doubao",
        "siliconflow",
    ]
    SUPPORTED_EMBEDDING = [
        "openai",
        "ollama",
        "dashscope",
        "zhipu",
        "google",
        "qianfan",
        "modelscope",
        "google-vertex",
        "doubao",
        "siliconflow",
    ]

    @staticmethod
    def get_reasoning_model(provider: str, model_name: str):
        provider = provider.lower()

        if provider not in ModelFactory.SUPPORTED_REASONING:
            raise ValueError(
                f"❌ 不支持的 Reasoning Provider: '{provider}'。目前 OneBase 支持: {ModelFactory.SUPPORTED_REASONING}"
            )

        if provider == "openai":
            from langchain_openai import ChatOpenAI

            api_base = _get_openai_base_url()
            return ChatOpenAI(
                model=model_name,
                streaming=True,
                base_url=api_base,
                api_key=os.getenv(
                    "OPENAI_API_KEY", "dummy-key"
                ),  # 本地推理框架通常不需要真实 Key
            )

        elif provider == "ollama":
            from langchain_ollama import ChatOllama

            base_url = _docker_rewrite(
                os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            )
            return ChatOllama(model=model_name, base_url=base_url, streaming=True)

        elif provider == "dashscope":
            # 💡 修正：阿里通义千问原生接口真实类名为 ChatTongyi
            from langchain_community.chat_models import ChatTongyi

            return ChatTongyi(
                model=model_name, streaming=True, api_key=os.getenv("DASHSCOPE_API_KEY")
            )

        elif provider == "zhipu":
            # 💡 修正：智谱原生接口
            from langchain_community.chat_models import ChatZhipuAI

            return ChatZhipuAI(
                model=model_name, streaming=True, api_key=os.getenv("ZHIPU_API_KEY")
            )

        elif provider == "anthropic":
            # Claude 原生接口
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(
                model_name=model_name,
                streaming=True,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            )

        elif provider == "google":
            # Google Gemini 原生接口
            from langchain_google_genai import ChatGoogleGenerativeAI

            return ChatGoogleGenerativeAI(
                model=model_name,
                streaming=True,
                google_api_key=os.getenv("GOOGLE_API_KEY"),
            )

        elif provider == "google-vertex":
            from langchain_google_vertexai import ChatVertexAI

            return ChatVertexAI(
                model=model_name,
                streaming=True,
                project=os.getenv("GOOGLE_CLOUD_PROJECT"),
                location=os.getenv("VERTEX_LOCATION", "us-central1"),
                credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            )

        elif provider == "qianfan":
            # 💡 修正：百度千帆原生接口真实类名
            from langchain_community.chat_models import QianfanChatEndpoint

            return QianfanChatEndpoint(
                model=model_name,
                streaming=True,
                qianfan_ak=os.getenv("QIANFAN_AK"),
                qianfan_sk=os.getenv("QIANFAN_SK"),
            )

        elif provider == "groq":
            # Groq LPU 极速推理
            from langchain_groq import ChatGroq

            return ChatGroq(
                model_name=model_name,
                groq_api_key=os.getenv("GROQ_API_KEY"),
                streaming=True,
            )

        elif provider == "deepseek":
            # 🌟 拥抱 LangChain 0.3+：使用独立的 langchain_deepseek 包
            from langchain_deepseek import ChatDeepSeek

            return ChatDeepSeek(
                model=model_name, streaming=True, api_key=os.getenv("DEEPSEEK_API_KEY")
            )

        elif provider == "modelscope":
            # ModelScopeChatEndpoint 支持类似 Qwen/Qwen2.5-Coder-32B-Instruct 的魔搭模型
            from langchain_modelscope import ModelScopeChatEndpoint

            return ModelScopeChatEndpoint(model=model_name, streaming=True)

        elif provider == "doubao":
            from langchain_community.chat_models import ChatVolcEngineMaas

            return ChatVolcEngineMaas(
                model=model_name,
                streaming=True,
                endpoint_id=os.getenv("VOLC_ENGINE_ENDPOINT_ID"),  # 火山方舟的接入点ID
                ak=os.getenv("VOLC_ACCESS_KEY"),  # 火山引擎的Access Key
                sk=os.getenv("VOLC_SECRET_KEY"),  # 火山引擎的Secret Key
            )
        elif provider == "siliconflow":
            from langchain_community.chat_models import ChatSiliconFlow

            return ChatSiliconFlow(
                model=model_name,
                streaming=True,
                siliconflow_api_key=os.getenv("SILICONFLOW_API_KEY"),
                base_url="https://api.siliconflow.cn/v1",  # 硅基流动的API地址
            )

    @staticmethod
    def get_embedding_model(provider: str, model_name: str):
        provider = provider.lower()

        if provider not in ModelFactory.SUPPORTED_EMBEDDING:
            raise ValueError(
                f"❌ 不支持的 Embedding Provider: '{provider}'。目前 OneBase 支持: {ModelFactory.SUPPORTED_EMBEDDING}"
            )

        if provider == "openai":
            from langchain_openai import OpenAIEmbeddings

            api_base = _get_openai_base_url()
            return OpenAIEmbeddings(
                model=model_name,
                api_key=os.getenv("OPENAI_API_KEY", "dummy-key"),
                base_url=api_base,
            )

        elif provider == "ollama":
            from langchain_ollama import OllamaEmbeddings

            base_url = _docker_rewrite(
                os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            )
            return OllamaEmbeddings(model=model_name, base_url=base_url)

        elif provider == "dashscope":
            # 阿里通义原生 Embedding
            from langchain_community.embeddings import DashScopeEmbeddings

            return DashScopeEmbeddings(
                model=model_name, dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")
            )

        elif provider == "zhipu":
            from langchain_community.embeddings import ZhipuAIEmbeddings

            return ZhipuAIEmbeddings(
                model=model_name, api_key=os.getenv("ZHIPU_API_KEY")
            )

        elif provider == "qianfan":
            from langchain_community.embeddings import QianfanEmbeddingsEndpoint

            return QianfanEmbeddingsEndpoint(
                model=model_name,
                qianfan_ak=os.getenv("QIANFAN_AK"),
                qianfan_sk=os.getenv("QIANFAN_SK"),
            )

        elif provider == "modelscope":
            # ModelScopeEmbeddings 支持如 damo/nlp_corom_sentence-embedding_english-base 等
            # 很多国内优秀的开源 BGE / 达摩院 向量模型都托管在这里
            from langchain_modelscope import ModelScopeEmbeddings

            return ModelScopeEmbeddings(model_id=model_name)

        elif provider == "google":
            from langchain_google_genai import GoogleGenerativeAIEmbeddings

            return GoogleGenerativeAIEmbeddings(
                model=model_name, google_api_key=os.getenv("GOOGLE_API_KEY")
            )

        elif provider == "google-vertex":
            from langchain_google_vertexai import VertexAIEmbeddings

            return VertexAIEmbeddings(
                model=model_name,
                project=os.getenv("GOOGLE_CLOUD_PROJECT"),
                location=os.getenv("VERTEX_LOCATION", "us-central1"),
                credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            )

        elif provider == "doubao":
            from langchain_community.embeddings import VolcEngineMaasEmbeddings

            return VolcEngineMaasEmbeddings(
                model=model_name,
                endpoint_id=os.getenv("VOLC_ENGINE_ENDPOINT_ID"),  # 火山方舟的接入点ID
                ak=os.getenv("VOLC_ACCESS_KEY"),  # 火山引擎的Access Key
                sk=os.getenv("VOLC_SECRET_KEY"),  # 火山引擎的Secret Key
            )
        elif provider == "siliconflow":
            from langchain_community.embeddings import SiliconFlowEmbeddings

            return SiliconFlowEmbeddings(
                model=model_name,
                siliconflow_api_key=os.getenv("SILICONFLOW_API_KEY"),
                base_url="https://api.siliconflow.cn/v1",  # 硅基流动的API地址
            )
