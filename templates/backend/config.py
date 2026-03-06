import os
import sys


def _get_bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).lower() == "true"


def _get_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


DB_URL = os.getenv("DATABASE_URL")

# 🌟 [1-7] 启动时校验必要的环境变量，防止 None 传入 SQLAlchemy 导致不明确的崩溃
if not DB_URL:
    print(
        "❌ 致命错误: 未设置 DATABASE_URL 环境变量。\n"
        "   请检查 Docker Compose 配置或 .env 文件。",
        file=sys.stderr,
    )
    sys.exit(1)

SITE_NAME = os.getenv("SITE_NAME", "OneBase AI")
REASONING_PROVIDER = os.getenv("REASONING_PROVIDER", "openai").lower()
REASONING_MODEL = os.getenv("REASONING_MODEL", "gpt-3.5-turbo")
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai").lower()
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# 🌟 [Step2] Feature Flags：从环境变量读取，源头是 onebase.yml → docker_runner → 环境变量
FEATURE_CHAT_HISTORY = _get_bool("FEATURE_CHAT_HISTORY", True)
FEATURE_FILE_UPLOAD = _get_bool("FEATURE_FILE_UPLOAD", True)

# 可选 Redis（缓存 / 限流）
REDIS_URL = os.getenv("REDIS_URL", "")
REDIS_CACHE_ENABLED = _get_bool("REDIS_CACHE_ENABLED", True)
REDIS_CONTEXT_CACHE_TTL_SECONDS = _get_int("REDIS_CONTEXT_CACHE_TTL_SECONDS", 300)

# 🔐 API Token 鉴权（可选）：设置后所有 /api/* 端点（除 /api/health）需携带 Authorization: Bearer <token>
API_TOKEN = os.getenv("API_TOKEN", "")

# 接口限流（固定窗口）
RATE_LIMIT_ENABLED = _get_bool("RATE_LIMIT_ENABLED", True)
CHAT_RATE_LIMIT_PER_MINUTE = _get_int("CHAT_RATE_LIMIT_PER_MINUTE", 30)
UPLOAD_RATE_LIMIT_PER_MINUTE = _get_int("UPLOAD_RATE_LIMIT_PER_MINUTE", 6)

# 日志格式："text"（默认 Rich 文本）或 "json"（结构化 JSON，适合日志聚合）
LOG_FORMAT = os.getenv("LOG_FORMAT", "text").lower()
