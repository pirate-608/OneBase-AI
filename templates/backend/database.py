import time
import logging
from sqlalchemy import (
    create_engine,
    text,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    func,
)
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DB_URL

logger = logging.getLogger("onebase.backend")

Base = declarative_base()

# =============================================
# 1. 声明式模型定义（纯声明，不依赖数据库连接）
# =============================================


class ChatMessageDB(Base):
    """聊天消息表"""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    role = Column(String, nullable=False)  # 'user' 或 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# 🌟 [1-6] 会话元数据表：用于存储用户自定义的会话标题
class ChatSessionMeta(Base):
    """会话元数据（如自定义标题）"""

    __tablename__ = "chat_session_meta"

    session_id = Column(String, primary_key=True)
    title = Column(String, nullable=True)


# =============================================
# 2. 🌟 [1-8] 懒初始化：延迟到首次请求时才建立连接
#    附带重试逻辑，应对 Docker Compose 启动时序问题
# =============================================

_engine = None
_SessionLocal = None


def _init_db(max_retries: int = 10, retry_interval: float = 2.0):
    """带重试的数据库初始化，应对 PG 容器尚未就绪的场景"""
    global _engine, _SessionLocal
    if _engine is not None:
        return

    for attempt in range(1, max_retries + 1):
        try:
            _engine = create_engine(DB_URL)
            # 尝试真正建立一次连接以验证 PG 是否 ready
            with _engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            _SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=_engine
            )
            Base.metadata.create_all(bind=_engine)
            logger.info("✅ 数据库连接成功")
            return
        except Exception as e:
            if attempt < max_retries:
                logger.warning(
                    f"⏳ 数据库连接失败 (尝试 {attempt}/{max_retries})，{retry_interval}s 后重试... ({e})"
                )
                time.sleep(retry_interval)
            else:
                raise RuntimeError(f"❌ 数据库连接失败，已重试 {max_retries} 次: {e}")


# 3. FastAPI 的依赖注入函数
def get_db():
    _init_db()
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🌟 [2-2] 暴露 _init_db 和 _SessionLocal 供流式生成器独立管理 session
# 通过模块级引用即可：from database import _init_db, _SessionLocal
