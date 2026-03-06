import json
import hashlib
import logging
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import func  # 🌟 新增：引入聚合函数
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from config import (
    SITE_NAME,
    FEATURE_CHAT_HISTORY,
)
from schemas import ChatRequest, RenameSessionRequest
from deps import get_embedding_model, get_reasoning_model, get_vector_store
from cache import get_cached_context, set_cached_context

# 🌟 引入数据库依赖（含会话元数据表）
# 🌟 [2-2] 同时引入 _init_db 和 _SessionLocal 供流式生成器独立管理 session
from database import get_db, ChatMessageDB, ChatSessionMeta, _init_db, _SessionLocal

router = APIRouter()
logger = logging.getLogger("onebase.backend")


def _build_context_cache_key(
    collection_name: str, search_query: str, k: int = 4
) -> str:
    digest = hashlib.sha256(search_query.encode("utf-8")).hexdigest()
    return f"ctx:{collection_name}:{k}:{digest}"


# 🌟 新增：获取历史会话列表接口
@router.get("/sessions")
def get_sessions(db: Session = Depends(get_db)):
    """获取所有历史会话列表"""
    # 按照会话中最后一条消息的时间降序排列
    sessions = (
        db.query(
            ChatMessageDB.session_id,
            func.max(ChatMessageDB.created_at).label("last_active"),
        )
        .group_by(ChatMessageDB.session_id)
        .order_by(func.max(ChatMessageDB.created_at).desc())
        .all()
    )

    result = []
    for sess in sessions:
        # 🌟 [1-6] 优先使用用户自定义的标题，否则取第一条用户消息自动生成
        meta = (
            db.query(ChatSessionMeta)
            .filter(ChatSessionMeta.session_id == sess.session_id)
            .first()
        )

        if meta and meta.title:
            title = meta.title
        else:
            first_msg = (
                db.query(ChatMessageDB)
                .filter(
                    ChatMessageDB.session_id == sess.session_id,
                    ChatMessageDB.role == "user",
                )
                .order_by(ChatMessageDB.created_at.asc())
                .first()
            )
            title = (
                first_msg.content[:15] + "..."
                if first_msg and len(first_msg.content) > 15
                else (first_msg.content if first_msg else "新对话")
            )

        result.append(
            {"id": sess.session_id, "title": title, "created_at": sess.last_active}
        )
    return result


# 🌟 [1-6] 重命名会话接口（对应前端 renameSession 调用）
@router.put("/sessions/{session_id}")
def rename_session(
    session_id: str, body: RenameSessionRequest, db: Session = Depends(get_db)
):
    """更新指定会话的自定义标题"""
    meta = (
        db.query(ChatSessionMeta)
        .filter(ChatSessionMeta.session_id == session_id)
        .first()
    )
    if meta:
        meta.title = body.title
    else:
        meta = ChatSessionMeta(session_id=session_id, title=body.title)
        db.add(meta)
    db.commit()
    return {"status": "success", "title": body.title}


@router.delete("/history/{session_id}")
def delete_chat_history(session_id: str, db: Session = Depends(get_db)):
    """删除指定会话的所有历史记录"""
    db.query(ChatMessageDB).filter(ChatMessageDB.session_id == session_id).delete()
    db.commit()
    logger.info("会话删除: session_id=%s", session_id)
    return {"status": "success"}


@router.get("/history/{session_id}")
def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    """获取指定会话的历史记录，按时间顺序排列"""
    messages = (
        db.query(ChatMessageDB)
        .filter(ChatMessageDB.session_id == session_id)
        .order_by(ChatMessageDB.created_at.asc())
        .all()
    )
    return [{"role": msg.role, "content": msg.content} for msg in messages]


@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest, db: Session = Depends(get_db)
):  # 🌟 注入数据库 Session
    user_query = request.messages[-1].content
    session_id = request.session_id

    # 💾 1. 立即将用户的最新问题存入数据库（仅在开启聊天历史时）
    if FEATURE_CHAT_HISTORY:
        db_user_msg = ChatMessageDB(
            session_id=session_id, role="user", content=user_query
        )
        db.add(db_user_msg)
        db.commit()

    # 2. 检索记忆拼接 (与之前保持一致)
    search_query = user_query
    if len(request.messages) > 1:
        last_ai_msg = next(
            (
                msg.content
                for msg in reversed(request.messages[:-1])
                if msg.role == "assistant"
            ),
            "",
        )
        context_anchor = last_ai_msg[:200] if last_ai_msg else ""
        search_query = f"背景语境: {context_anchor}\n用户问题: {user_query}"

    # 3. 向量检索
    collection_name = SITE_NAME.replace(" ", "_").lower()
    vector_store = get_vector_store()

    context_cache_key = _build_context_cache_key(collection_name, search_query, k=4)
    context_text = get_cached_context(context_cache_key)

    if not context_text:
        retrieved_docs = vector_store.similarity_search(search_query, k=4)
        context_text = "\n\n".join(
            f"[来源: {doc.metadata.get('breadcrumbs', '未知')}]\n{doc.page_content}"
            for doc in retrieved_docs
        )
        set_cached_context(context_cache_key, context_text)

    # 4. 构建 Prompt
    system_prompt = f"""你是一个名为 "{SITE_NAME}" 的专属 AI 助手。
请**基于以下参考资料**以及**我们的对话历史**来回答用户的问题。如果资料中没有，请诚实说明。
【参考资料】
{context_text}
"""

    langchain_messages = [SystemMessage(content=system_prompt)]
    for msg in request.messages[:-1]:
        if msg.role == "user":
            langchain_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            langchain_messages.append(AIMessage(content=msg.content))

    langchain_messages.append(HumanMessage(content=user_query))

    # 5. 模型调用与流式返回
    llm = get_reasoning_model()

    async def generate_stream():
        full_response = ""
        try:
            async for chunk in llm.astream(langchain_messages):
                if chunk.content:
                    full_response += chunk.content
                    yield f"data: {json.dumps({'content': chunk.content})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            # 💾 [2-2] 流式生成器独立管理 DB Session
            # 外层 Depends(get_db) 注入的 db 可能已被 FastAPI 关闭，
            # 因此在 finally 中创建独立 session 存储 AI 回复，避免生命周期泄漏
            # 🌟 [Step2] 仅在开启聊天历史时持久化 AI 回复
            if FEATURE_CHAT_HISTORY and full_response.strip():
                try:
                    _init_db()
                    with _SessionLocal() as db_inner:
                        db_ai_msg = ChatMessageDB(
                            session_id=session_id,
                            role="assistant",
                            content=full_response,
                        )
                        db_inner.add(db_ai_msg)
                        db_inner.commit()
                except Exception as db_err:
                    import logging

                    logging.getLogger("onebase.backend").error(
                        f"保存 AI 回复失败: {db_err}"
                    )

    return StreamingResponse(generate_stream(), media_type="text/event-stream")
