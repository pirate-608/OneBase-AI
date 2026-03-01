import logging
from rich.logging import RichHandler
from rich.console import Console

# 🌟 全局共用的 Console 实例（用于渲染进度条、表格和面板）
console = Console()
# 专门用于向 stderr 打印错误（避免污染输出管道）
err_console = Console(stderr=True)

def setup_logger(level_name: str = "INFO"):
    """
    配置全局日志级别与 Rich 呈现格式
    """
    level = getattr(logging, level_name.upper(), logging.INFO)
    
    # 核心逻辑 1：如果在 ERROR(静默) 级别，关闭所有基于 console 的富文本渲染（进度条、表格等将不再显示）
    console.quiet = (level >= logging.ERROR)
    
    # 核心逻辑 2：仅在 DEBUG 模式下，才显示时间戳、文件路径和级别标签。INFO 模式保持干净纯粹的交互。
    show_details = (level == logging.DEBUG)

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=console,
                rich_tracebacks=True,
                markup=True,
                show_time=show_details,
                show_level=show_details,
                show_path=show_details
            )
        ],
        force=True # 强制覆盖并接管系统的 root logger
    )

# 导出单例 logger，供所有子模块调用
logger = logging.getLogger("onebase")

# 默认进行一次标准初始化
setup_logger("INFO")