"""
OneBase: 像配置静态网站一样，一键构建与部署 AI 动态服务。
"""

# 🌟 [1-1] 版本号统一从 pyproject.toml 获取（唯一真相源）
# 不再硬编码版本号，避免多处不一致
try:
    from importlib.metadata import version

    __version__ = version("onebase-ai")
except Exception:
    __version__ = "dev"

# 将 CLI 的核心 Typer 应用暴露出来
# 这样在打包时，可以直接指向 onebase.app
from .cli import app

# 明确声明允许被外部 import 的对象
__all__ = ["app", "__version__"]
