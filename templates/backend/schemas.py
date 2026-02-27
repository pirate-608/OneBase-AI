from pydantic import BaseModel
from typing import List

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    session_id: str = "default-session"  # 🌟 新增：会话标识
    messages: List[ChatMessage]
    stream: bool = True