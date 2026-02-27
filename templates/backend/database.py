from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DB_URL

# 1. 初始化 SQLAlchemy 引擎
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. 定义聊天记录表模型
class ChatMessageDB(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False) # 用于区分不同的用户或会话
    role = Column(String, nullable=False)                   # 'user' 或 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# 3. 自动创建表结构（如果表不存在，启动时会自动在 Postgres 中建表）
Base.metadata.create_all(bind=engine)

# 4. FastAPI 的依赖注入函数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()