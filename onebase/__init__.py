"""
OneBase: 像配置静态网站一样，一键构建与部署 AI 动态服务。
"""

# 定义包的版本号
__version__ = "0.1.0"

# 将 CLI 的核心 Typer 应用暴露出来
# 这样在打包时，可以直接指向 onebase.app
from .cli import app

# 明确声明允许被外部 import 的对象
__all__ = ["app", "__version__"]