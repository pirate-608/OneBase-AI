import json
import logging
from typing import Optional

from config import REDIS_CACHE_ENABLED, REDIS_CONTEXT_CACHE_TTL_SECONDS, REDIS_URL

logger = logging.getLogger("onebase.backend")
_redis_client = None


def _get_redis_client():
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    if not REDIS_CACHE_ENABLED or not REDIS_URL:
        return None

    try:
        import redis

        _redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        _redis_client.ping()
        logger.info("✅ Redis cache connected")
        return _redis_client
    except Exception as e:
        logger.warning(f"Redis cache unavailable, fallback to direct retrieval: {e}")
        _redis_client = None
        return None


def get_cached_context(cache_key: str) -> Optional[str]:
    client = _get_redis_client()
    if client is None:
        return None
    try:
        payload = client.get(cache_key)
        if not payload:
            return None
        data = json.loads(payload)
        return data.get("context_text")
    except Exception as e:
        logger.warning(f"Redis get cache failed: {e}")
        return None


def set_cached_context(cache_key: str, context_text: str):
    client = _get_redis_client()
    if client is None:
        return
    try:
        payload = json.dumps({"context_text": context_text}, ensure_ascii=False)
        client.setex(cache_key, REDIS_CONTEXT_CACHE_TTL_SECONDS, payload)
    except Exception as e:
        logger.warning(f"Redis set cache failed: {e}")
