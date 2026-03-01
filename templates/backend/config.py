import os
import sys

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
FEATURE_CHAT_HISTORY = os.getenv("FEATURE_CHAT_HISTORY", "true").lower() == "true"
FEATURE_FILE_UPLOAD = os.getenv("FEATURE_FILE_UPLOAD", "true").lower() == "true"
