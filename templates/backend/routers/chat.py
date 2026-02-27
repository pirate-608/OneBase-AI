import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_postgres.vectorstores import PGVector

from config import SITE_NAME, DB_URL, EMBEDDING_PROVIDER, EMBEDDING_MODEL, REASONING_PROVIDER, REASONING_MODEL
from schemas import ChatRequest
from factory import ModelFactory
# 🌟 引入我们刚才写的数据库依赖
from database import get_db, ChatMessageDB 

router = APIRouter()

@router.get("/history/{session_id}")
def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    """获取指定会话的历史记录，按时间顺序排列"""
    messages = db.query(ChatMessageDB).filter(ChatMessageDB.session_id == session_id).order_by(ChatMessageDB.created_at.asc()).all()
    return [{"role": msg.role, "content": msg.content} for msg in messages]

@router.post("/chat")
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)): # 🌟 注入数据库 Session
    user_query = request.messages[-1].content
    session_id = request.session_id
    
    # 💾 1. 立即将用户的最新问题存入数据库
    db_user_msg = ChatMessageDB(session_id=session_id, role="user", content=user_query)
    db.add(db_user_msg)
    db.commit()

    # 2. 检索记忆拼接 (与之前保持一致)
    search_query = user_query
    if len(request.messages) > 1:
        last_ai_msg = next((msg.content for msg in reversed(request.messages[:-1]) if msg.role == "assistant"), "")
        context_anchor = last_ai_msg[:200] if last_ai_msg else ""
        search_query = f"背景语境: {context_anchor}\n用户问题: {user_query}"

    # 3. 向量检索
    embeddings = ModelFactory.get_embedding_model(EMBEDDING_PROVIDER, EMBEDDING_MODEL)
    collection_name = SITE_NAME.replace(" ", "_").lower()
    
    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=DB_URL,
        use_jsonb=True,
    )
    
    retrieved_docs = vector_store.similarity_search(search_query, k=4)
    context_text = "\n\n".join(
        f"[来源: {doc.metadata.get('breadcrumbs', '未知')}]\n{doc.page_content}" 
        for doc in retrieved_docs
    )

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
    llm = ModelFactory.get_reasoning_model(REASONING_PROVIDER, REASONING_MODEL)

    async def generate_stream():
        full_response = ""
        try:
            async for chunk in llm.astream(langchain_messages):
                if chunk.content:
                    full_response += chunk.content # 🌟 拼接 AI 吐出的每一个字
                    yield f"data: {json.dumps({'content': chunk.content})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            # 💾 6. 终极保险：无论正常结束还是用户中途关掉网页，都把收集到的 AI 完整回复存入数据库
            if full_response.strip():
                db_ai_msg = ChatMessageDB(session_id=session_id, role="assistant", content=full_response)
                db.add(db_ai_msg)
                db.commit()

    return StreamingResponse(generate_stream(), media_type="text/event-stream")