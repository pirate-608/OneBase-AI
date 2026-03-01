from pydantic import BaseModel
from typing import List


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    session_id: str = "default-session"
    messages: List[ChatMessage]
    stream: bool = True


# 🌟 [1-6] 会话重命名请求体
class RenameSessionRequest(BaseModel):
    title: str
