import logging
import threading
import time
from collections import defaultdict
from typing import Tuple

from config import RATE_LIMIT_ENABLED, REDIS_URL

logger = logging.getLogger("onebase.backend")


class FixedWindowRateLimiter:
    def __init__(self):
        self.enabled = RATE_LIMIT_ENABLED
        self._local_counter = defaultdict(int)
        self._local_expire_at = {}
        self._lock = threading.Lock()
        self._redis = self._init_redis()

    def _init_redis(self):
        if not self.enabled or not REDIS_URL:
            return None
        try:
            import redis

            client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
            client.ping()
            logger.info("✅ Redis rate limiter connected")
            return client
        except Exception as e:
            logger.warning(f"Redis rate limiter unavailable, fallback to local: {e}")
            return None

    def allow(
        self, bucket: str, subject: str, limit: int, window_sec: int
    ) -> Tuple[bool, int]:
        if not self.enabled:
            return True, 0
        if limit <= 0 or window_sec <= 0:
            return True, 0

        window_start = int(time.time()) // window_sec
        key = f"rl:{bucket}:{subject}:{window_start}"

        if self._redis is not None:
            try:
                count = self._redis.incr(key)
                if count == 1:
                    self._redis.expire(key, window_sec)
                if count <= limit:
                    return True, 0
                retry_after = max(self._redis.ttl(key), 1)
                return False, retry_after
            except Exception as e:
                logger.warning(f"Redis rate limiter error, fallback to local: {e}")

        now = int(time.time())
        with self._lock:
            expire_at = self._local_expire_at.get(key, 0)
            if now >= expire_at:
                self._local_counter[key] = 0
                self._local_expire_at[key] = now + window_sec

            self._local_counter[key] += 1
            count = self._local_counter[key]
            if count <= limit:
                return True, 0

            retry_after = max(self._local_expire_at[key] - now, 1)
            return False, retry_after
