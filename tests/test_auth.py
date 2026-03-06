"""Tests for API Token authentication middleware (P0#2).

Uses a self-contained FastAPI app that replicates the exact auth middleware
logic from main.py, avoiding the need to import the full backend stack.
"""

import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.testclient import TestClient


def _create_test_app(api_token: str = ""):
    """Create a minimal FastAPI app with the same auth middleware logic as main.py."""
    app = FastAPI()

    _auth_whitelist = {"/api/health"}

    @app.middleware("http")
    async def apply_auth(request, call_next):
        path = request.url.path
        if api_token and path.startswith("/api/") and path not in _auth_whitelist:
            auth_header = request.headers.get("authorization", "")
            if not auth_header.startswith("Bearer ") or auth_header[7:] != api_token:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "未授权访问，请提供有效的 API Token"},
                    headers={"WWW-Authenticate": "Bearer"},
                )
        return await call_next(request)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.get("/api/sessions")
    def sessions():
        return [{"id": "s1", "title": "test"}]

    @app.post("/api/chat")
    def chat():
        return {"content": "hello"}

    return app


class TestAuthMiddleware:
    def test_health_always_public(self):
        """Health endpoint should never require auth, even with token set."""
        client = TestClient(_create_test_app(api_token="secret-token-123"))
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_no_token_configured_allows_all(self):
        """When API_TOKEN is empty, all endpoints are open."""
        client = TestClient(_create_test_app(api_token=""))
        resp = client.get("/api/sessions")
        assert resp.status_code == 200

    def test_missing_token_returns_401(self):
        """Request without Authorization header should get 401."""
        client = TestClient(_create_test_app(api_token="my-secret"))
        resp = client.get("/api/sessions")
        assert resp.status_code == 401
        assert "未授权" in resp.json()["detail"]

    def test_wrong_token_returns_401(self):
        """Request with wrong token should get 401."""
        client = TestClient(_create_test_app(api_token="correct-token"))
        resp = client.get(
            "/api/sessions", headers={"Authorization": "Bearer wrong-token"}
        )
        assert resp.status_code == 401

    def test_correct_token_passes(self):
        """Request with correct token should pass auth middleware."""
        client = TestClient(_create_test_app(api_token="correct-token"))
        resp = client.get(
            "/api/sessions", headers={"Authorization": "Bearer correct-token"}
        )
        assert resp.status_code == 200
        assert resp.json()[0]["id"] == "s1"

    def test_bearer_prefix_required(self):
        """Token without 'Bearer ' prefix should be rejected."""
        client = TestClient(_create_test_app(api_token="my-token"))
        resp = client.get("/api/sessions", headers={"Authorization": "my-token"})
        assert resp.status_code == 401

    def test_www_authenticate_header(self):
        """401 response should include WWW-Authenticate: Bearer header."""
        client = TestClient(_create_test_app(api_token="my-token"))
        resp = client.get("/api/sessions")
        assert resp.status_code == 401
        assert resp.headers.get("www-authenticate") == "Bearer"

    def test_post_endpoint_requires_token(self):
        """POST endpoints should also require token."""
        client = TestClient(_create_test_app(api_token="secret"))
        resp = client.post("/api/chat")
        assert resp.status_code == 401

        resp = client.post("/api/chat", headers={"Authorization": "Bearer secret"})
        assert resp.status_code == 200

    def test_non_api_paths_no_auth(self):
        """Non-/api/ paths should not require auth."""
        app = _create_test_app(api_token="secret")

        @app.get("/other")
        def other():
            return {"ok": True}

        client = TestClient(app)
        resp = client.get("/other")
        assert resp.status_code == 200
