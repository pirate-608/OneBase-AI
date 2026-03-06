"""Tests for Pydantic schema validation (P0#3 hardening)."""

import pytest
from pydantic import ValidationError
from onebase.config import OneBaseConfig

# schemas.py is in templates/backend, import requires path setup
import sys
from pathlib import Path

_backend_dir = str(Path(__file__).resolve().parent.parent / "templates" / "backend")
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

# Mock config module to avoid DATABASE_URL sys.exit
import types

fake_config = types.ModuleType("config")
fake_config.DB_URL = "postgresql://test:test@localhost/test"
fake_config.RATE_LIMIT_ENABLED = False
fake_config.REDIS_URL = None
fake_config.API_TOKEN = ""
sys.modules.setdefault("config", fake_config)

from schemas import ChatMessage, ChatRequest, RenameSessionRequest


class TestChatMessage:
    def test_valid_user_role(self):
        msg = ChatMessage(role="user", content="hello")
        assert msg.role == "user"

    def test_valid_assistant_role(self):
        msg = ChatMessage(role="assistant", content="hi there")
        assert msg.role == "assistant"

    def test_invalid_role_rejected(self):
        with pytest.raises(ValidationError):
            ChatMessage(role="system", content="test")

    def test_invalid_role_arbitrary(self):
        with pytest.raises(ValidationError):
            ChatMessage(role="admin", content="test")

    def test_empty_content_rejected(self):
        with pytest.raises(ValidationError):
            ChatMessage(role="user", content="")

    def test_content_max_length(self):
        """Content exceeding 50000 chars should be rejected."""
        with pytest.raises(ValidationError):
            ChatMessage(role="user", content="x" * 50001)

    def test_content_at_max_length(self):
        msg = ChatMessage(role="user", content="x" * 50000)
        assert len(msg.content) == 50000


class TestChatRequest:
    def test_default_session_id(self):
        req = ChatRequest(messages=[ChatMessage(role="user", content="hi")])
        assert req.session_id == "default-session"

    def test_custom_session_id(self):
        req = ChatRequest(
            session_id="session_abc123",
            messages=[ChatMessage(role="user", content="hi")],
        )
        assert req.session_id == "session_abc123"

    def test_session_id_max_length(self):
        with pytest.raises(ValidationError):
            ChatRequest(
                session_id="x" * 129,
                messages=[ChatMessage(role="user", content="hi")],
            )

    def test_session_id_special_chars_rejected(self):
        """Only alphanumeric, hyphens, underscores allowed."""
        with pytest.raises(ValidationError):
            ChatRequest(
                session_id="session/../../etc",
                messages=[ChatMessage(role="user", content="hi")],
            )

    def test_session_id_spaces_rejected(self):
        with pytest.raises(ValidationError):
            ChatRequest(
                session_id="session with spaces",
                messages=[ChatMessage(role="user", content="hi")],
            )

    def test_empty_messages_rejected(self):
        with pytest.raises(ValidationError):
            ChatRequest(messages=[])

    def test_session_id_allows_hyphens_underscores(self):
        req = ChatRequest(
            session_id="my-session_01",
            messages=[ChatMessage(role="user", content="hi")],
        )
        assert req.session_id == "my-session_01"


class TestRenameSessionRequest:
    def test_valid_title(self):
        req = RenameSessionRequest(title="My Chat")
        assert req.title == "My Chat"

    def test_empty_title_rejected(self):
        with pytest.raises(ValidationError):
            RenameSessionRequest(title="")

    def test_title_max_length(self):
        with pytest.raises(ValidationError):
            RenameSessionRequest(title="x" * 101)

    def test_title_at_max_length(self):
        req = RenameSessionRequest(title="x" * 100)
        assert len(req.title) == 100
