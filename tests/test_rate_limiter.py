"""Tests for FixedWindowRateLimiter (local-only, no Redis)."""

import pytest
import time
import sys
from pathlib import Path
from unittest.mock import patch

# rate_limiter.py is in templates/backend, not a pip-installed package.
# We need to add it to sys.path and mock its config imports.
_backend_dir = str(Path(__file__).resolve().parent.parent / "templates" / "backend")


def _import_rate_limiter():
    """Import rate_limiter with mocked config values."""
    with patch.dict("sys.modules", {}):
        if _backend_dir not in sys.path:
            sys.path.insert(0, _backend_dir)
        # Pre-populate the config module that rate_limiter will import
        import types

        fake_config = types.ModuleType("config")
        fake_config.RATE_LIMIT_ENABLED = True
        fake_config.REDIS_URL = None  # force local-only mode
        sys.modules["config"] = fake_config

        # Remove cached version if any
        sys.modules.pop("rate_limiter", None)

        from rate_limiter import FixedWindowRateLimiter

        return FixedWindowRateLimiter


class TestFixedWindowRateLimiter:
    def test_allows_under_limit(self):
        cls = _import_rate_limiter()
        rl = cls()
        allowed, _ = rl.allow("chat", "user1", limit=5, window_sec=60)
        assert allowed is True

    def test_blocks_over_limit(self):
        cls = _import_rate_limiter()
        rl = cls()
        for _ in range(5):
            rl.allow("chat", "user2", limit=5, window_sec=60)
        allowed, retry_after = rl.allow("chat", "user2", limit=5, window_sec=60)
        assert allowed is False
        assert retry_after > 0

    def test_disabled_always_allows(self):
        """When rate limiting is disabled, always allow."""
        with patch.dict("sys.modules", {}):
            if _backend_dir not in sys.path:
                sys.path.insert(0, _backend_dir)
            import types

            fake_config = types.ModuleType("config")
            fake_config.RATE_LIMIT_ENABLED = False
            fake_config.REDIS_URL = None
            sys.modules["config"] = fake_config
            sys.modules.pop("rate_limiter", None)

            from rate_limiter import FixedWindowRateLimiter

            rl = FixedWindowRateLimiter()
            for _ in range(100):
                allowed, _ = rl.allow("chat", "user3", limit=1, window_sec=60)
                assert allowed is True

    def test_different_buckets_independent(self):
        cls = _import_rate_limiter()
        rl = cls()
        for _ in range(5):
            rl.allow("chat", "user4", limit=5, window_sec=60)
        # chat bucket is exhausted
        allowed_chat, _ = rl.allow("chat", "user4", limit=5, window_sec=60)
        assert allowed_chat is False
        # upload bucket should be fine
        allowed_upload, _ = rl.allow("upload", "user4", limit=5, window_sec=60)
        assert allowed_upload is True

    def test_zero_limit_always_allows(self):
        cls = _import_rate_limiter()
        rl = cls()
        allowed, _ = rl.allow("test", "user5", limit=0, window_sec=60)
        assert allowed is True
