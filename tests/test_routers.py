"""Integration tests for backend router endpoints (P2#3).

Uses self-contained FastAPI apps that replicate router logic,
avoiding the need to import the full backend stack with DB/model deps.
"""

import io
import pytest
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.testclient import TestClient


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _create_app_with_auth_and_routes(api_token: str = ""):
    """Create a test app with auth middleware + typical route stubs."""
    app = FastAPI()

    _auth_whitelist = {"/api/health"}

    @app.middleware("http")
    async def apply_auth(request: Request, call_next):
        path = request.url.path
        if api_token and path.startswith("/api/") and path not in _auth_whitelist:
            auth_header = request.headers.get("authorization", "")
            if not auth_header.startswith("Bearer ") or auth_header[7:] != api_token:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Unauthorized"},
                    headers={"WWW-Authenticate": "Bearer"},
                )
        return await call_next(request)

    # --- health ---
    @app.get("/api/health")
    def health():
        return {
            "status": "ok",
            "site_name": "Test",
            "features": {"chat_history": True, "file_upload": True},
        }

    # --- tree ---
    @app.get("/api/tree")
    def tree():
        return [
            {"title": "section1", "type": "folder", "isOpen": False, "children": []},
            {"title": "readme", "type": "file", "path": "readme.md"},
        ]

    # --- file ---
    @app.get("/api/file/{file_path:path}")
    def get_file(file_path: str):
        if ".." in file_path:
            raise HTTPException(status_code=403, detail="禁止跨目录访问")
        return {"content": f"# Content of {file_path}"}

    # --- sessions ---
    _sessions = {"s1": "First Chat"}

    @app.get("/api/sessions")
    def sessions():
        return [{"id": k, "title": v} for k, v in _sessions.items()]

    @app.put("/api/sessions/{session_id}")
    def rename_session(session_id: str):
        return {"status": "success", "title": "renamed"}

    # --- history ---
    @app.get("/api/history/{session_id}")
    def get_history(session_id: str):
        return [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "hello"},
        ]

    @app.delete("/api/history/{session_id}")
    def delete_history(session_id: str):
        return {"status": "success"}

    # --- chat (simplified, no streaming) ---
    @app.post("/api/chat")
    def chat(request: dict):
        msgs = request.get("messages", [])
        if not msgs:
            raise HTTPException(status_code=422, detail="messages required")
        return {"content": "This is the AI reply."}

    # --- upload ---
    @app.post("/api/upload")
    def upload(file: UploadFile = File(...)):
        ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename else ""
        if ext not in ("pdf", "txt", "md"):
            raise HTTPException(status_code=400, detail="Unsupported format")
        contents = file.file.read()
        if len(contents) > 20 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large")
        return {"status": "success", "filename": file.filename, "chunks": 3}

    return app


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def client():
    """Client with no auth required."""
    return TestClient(_create_app_with_auth_and_routes(api_token=""))


@pytest.fixture
def auth_client():
    """Client with auth required; provides a helper for authed requests."""
    app = _create_app_with_auth_and_routes(api_token="test-token-xyz")
    c = TestClient(app)
    c._auth_headers = {"Authorization": "Bearer test-token-xyz"}
    return c


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------


class TestHealthEndpoint:
    def test_returns_ok(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "features" in data

    def test_returns_site_name(self, client):
        resp = client.get("/api/health")
        assert resp.json()["site_name"] == "Test"

    def test_feature_flags_present(self, client):
        resp = client.get("/api/health")
        features = resp.json()["features"]
        assert "chat_history" in features
        assert "file_upload" in features


# ---------------------------------------------------------------------------
# Tree endpoint
# ---------------------------------------------------------------------------


class TestTreeEndpoint:
    def test_returns_list(self, client):
        resp = client.get("/api/tree")
        assert resp.status_code == 200
        tree = resp.json()
        assert isinstance(tree, list)
        assert len(tree) >= 1

    def test_folder_structure(self, client):
        resp = client.get("/api/tree")
        folder = next(n for n in resp.json() if n["type"] == "folder")
        assert "children" in folder
        assert "isOpen" in folder

    def test_file_structure(self, client):
        resp = client.get("/api/tree")
        file_node = next(n for n in resp.json() if n["type"] == "file")
        assert "path" in file_node

    def test_requires_auth_when_enabled(self, auth_client):
        resp = auth_client.get("/api/tree")
        assert resp.status_code == 401
        resp = auth_client.get("/api/tree", headers=auth_client._auth_headers)
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# File endpoint
# ---------------------------------------------------------------------------


class TestFileEndpoint:
    def test_returns_content(self, client):
        resp = client.get("/api/file/readme.md")
        assert resp.status_code == 200
        assert "content" in resp.json()

    def test_path_traversal_blocked(self, client):
        # The route checks for ".." in the path to block traversal
        resp = client.get("/api/file/section1/..%2F..%2Fetc/passwd")
        assert resp.status_code == 403

    def test_nested_path(self, client):
        resp = client.get("/api/file/section1/overview.md")
        assert resp.status_code == 200
        assert "section1/overview.md" in resp.json()["content"]


# ---------------------------------------------------------------------------
# Sessions endpoint
# ---------------------------------------------------------------------------


class TestSessionsEndpoint:
    def test_list_sessions(self, client):
        resp = client.get("/api/sessions")
        assert resp.status_code == 200
        sessions = resp.json()
        assert isinstance(sessions, list)
        assert sessions[0]["id"] == "s1"

    def test_rename_session(self, client):
        resp = client.put("/api/sessions/s1")
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"


# ---------------------------------------------------------------------------
# History endpoint
# ---------------------------------------------------------------------------


class TestHistoryEndpoint:
    def test_get_history(self, client):
        resp = client.get("/api/history/s1")
        assert resp.status_code == 200
        messages = resp.json()
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"

    def test_delete_history(self, client):
        resp = client.delete("/api/history/s1")
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"


# ---------------------------------------------------------------------------
# Chat endpoint
# ---------------------------------------------------------------------------


class TestChatEndpoint:
    def test_post_chat(self, client):
        resp = client.post(
            "/api/chat",
            json={
                "session_id": "s1",
                "messages": [{"role": "user", "content": "hello"}],
            },
        )
        assert resp.status_code == 200
        assert "content" in resp.json()

    def test_empty_messages_rejected(self, client):
        resp = client.post(
            "/api/chat",
            json={
                "session_id": "s1",
                "messages": [],
            },
        )
        assert resp.status_code == 422

    def test_chat_requires_auth(self, auth_client):
        resp = auth_client.post(
            "/api/chat",
            json={
                "messages": [{"role": "user", "content": "hi"}],
            },
        )
        assert resp.status_code == 401
        resp = auth_client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "hi"}]},
            headers=auth_client._auth_headers,
        )
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Upload endpoint
# ---------------------------------------------------------------------------


class TestUploadEndpoint:
    def test_upload_txt(self, client):
        resp = client.post(
            "/api/upload",
            files={"file": ("notes.txt", io.BytesIO(b"hello world"), "text/plain")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["filename"] == "notes.txt"

    def test_upload_md(self, client):
        resp = client.post(
            "/api/upload",
            files={"file": ("doc.md", io.BytesIO(b"# Title"), "text/markdown")},
        )
        assert resp.status_code == 200

    def test_upload_unsupported_format(self, client):
        resp = client.post(
            "/api/upload",
            files={
                "file": (
                    "hack.exe",
                    io.BytesIO(b"\x00\x01"),
                    "application/octet-stream",
                )
            },
        )
        assert resp.status_code == 400

    def test_upload_requires_auth(self, auth_client):
        resp = auth_client.post(
            "/api/upload",
            files={"file": ("test.txt", io.BytesIO(b"data"), "text/plain")},
        )
        assert resp.status_code == 401
        resp = auth_client.post(
            "/api/upload",
            files={"file": ("test.txt", io.BytesIO(b"data"), "text/plain")},
            headers=auth_client._auth_headers,
        )
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Request ID middleware
# ---------------------------------------------------------------------------


class TestRequestIdMiddleware:
    def _make_app(self):
        """Minimal app with request-id middleware."""
        import uuid

        app = FastAPI()

        @app.middleware("http")
        async def add_request_id(request: Request, call_next):
            rid = request.headers.get("x-request-id", uuid.uuid4().hex[:12])
            response = await call_next(request)
            response.headers["X-Request-ID"] = rid
            return response

        @app.get("/api/health")
        def health():
            return {"status": "ok"}

        return app

    def test_auto_generated_request_id(self):
        client = TestClient(self._make_app())
        resp = client.get("/api/health")
        assert "x-request-id" in resp.headers
        assert len(resp.headers["x-request-id"]) == 12

    def test_custom_request_id_passthrough(self):
        client = TestClient(self._make_app())
        resp = client.get("/api/health", headers={"X-Request-ID": "custom-rid-123"})
        assert resp.headers["x-request-id"] == "custom-rid-123"


# ---------------------------------------------------------------------------
# Rate limiting (logic test)
# ---------------------------------------------------------------------------


class TestRateLimitIntegration:
    def _make_app(self, limit: int = 3):
        """App with a simple in-memory rate limiter on /api/chat."""
        from collections import defaultdict

        counters = defaultdict(int)

        app = FastAPI()

        @app.middleware("http")
        async def rate_limit(request: Request, call_next):
            if request.url.path == "/api/chat":
                host = request.client.host if request.client else "unknown"
                counters[host] += 1
                if counters[host] > limit:
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Too many requests"},
                        headers={"Retry-After": "60"},
                    )
            return await call_next(request)

        @app.post("/api/chat")
        def chat():
            return {"content": "ok"}

        return app

    def test_allows_under_limit(self):
        client = TestClient(self._make_app(limit=5))
        for _ in range(5):
            resp = client.post("/api/chat")
            assert resp.status_code == 200

    def test_blocks_over_limit(self):
        client = TestClient(self._make_app(limit=2))
        client.post("/api/chat")
        client.post("/api/chat")
        resp = client.post("/api/chat")
        assert resp.status_code == 429
        assert "Retry-After" in resp.headers
