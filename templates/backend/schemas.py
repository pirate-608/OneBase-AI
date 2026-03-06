from pydantic import BaseModel, Field
from typing import List, Literal


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=50000)


class ChatRequest(BaseModel):
    session_id: str = Field(
        default="default-session",
        min_length=1,
        max_length=128,
        pattern=r"^[a-zA-Z0-9_\-]+$",
    )
    messages: List[ChatMessage] = Field(..., min_length=1)
    stream: bool = True


# 🌟 [1-6] 会话重命名请求体
class RenameSessionRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
