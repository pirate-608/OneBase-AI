"""
数据库连接字符串的单一来源 (Single Source of Truth)。

所有需要构建 PostgreSQL 连接字符串的模块统一调用此处的函数，
消除凭据硬编码和重复拼接。
"""

import os
from dotenv import load_dotenv


def _load_env() -> None:
    """确保 .env 已加载（幂等操作）"""
    load_dotenv()


def get_db_credentials() -> dict:
    """
    从环境变量读取数据库凭据，返回标准化字典。

    支持的环境变量:
        POSTGRES_USER     — 用户名，默认 onebase
        POSTGRES_PASSWORD — 密码，**必须设置**（onebase init 时自动生成）
        POSTGRES_DB       — 数据库名，默认 onebase_db
        POSTGRES_HOST     — 主机地址（CLI 侧自动使用 localhost）
        POSTGRES_PORT     — 端口，默认 5432
    """
    _load_env()

    return {
        "user": os.getenv("POSTGRES_USER", "onebase"),
        "password": os.getenv("POSTGRES_PASSWORD", ""),
        "dbname": os.getenv("POSTGRES_DB", "onebase_db"),
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
    }


def build_db_url(host_override: str | None = None) -> str:
    """
    构建 PostgreSQL 连接字符串。

    Args:
        host_override: 覆盖主机地址。Docker Compose 内部网络使用 "db"，
                       CLI 宿主机侧使用 "localhost"（默认）。

    Returns:
        格式: postgresql+psycopg://user:pass@host:port/dbname
    """
    creds = get_db_credentials()
    host = host_override or creds["host"]
    port = creds["port"]
    return f"postgresql+psycopg://{creds['user']}:{creds['password']}@{host}:{port}/{creds['dbname']}"
