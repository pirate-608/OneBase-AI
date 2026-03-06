"""
Application-level singletons for expensive resources.

Avoids re-creating LLM, Embedding, and PGVector instances on every request.
All objects are lazily initialized on first access and reused thereafter.
"""

import threading
from langchain_postgres.vectorstores import PGVector

from config import (
    SITE_NAME,
    DB_URL,
    EMBEDDING_PROVIDER,
    EMBEDDING_MODEL,
    REASONING_PROVIDER,
    REASONING_MODEL,
)
from factory import ModelFactory

_lock = threading.Lock()

_embedding_model = None
_reasoning_model = None
_vector_store = None


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        with _lock:
            if _embedding_model is None:
                _embedding_model = ModelFactory.get_embedding_model(
                    EMBEDDING_PROVIDER, EMBEDDING_MODEL
                )
    return _embedding_model


def get_reasoning_model():
    global _reasoning_model
    if _reasoning_model is None:
        with _lock:
            if _reasoning_model is None:
                _reasoning_model = ModelFactory.get_reasoning_model(
                    REASONING_PROVIDER, REASONING_MODEL
                )
    return _reasoning_model


def get_vector_store() -> PGVector:
    global _vector_store
    if _vector_store is None:
        with _lock:
            if _vector_store is None:
                collection_name = SITE_NAME.replace(" ", "_").lower()
                _vector_store = PGVector(
                    embeddings=get_embedding_model(),
                    collection_name=collection_name,
                    connection=DB_URL,
                    use_jsonb=True,
                )
    return _vector_store
