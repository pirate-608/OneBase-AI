import os
import uuid
import time
import logging
from contextvars import ContextVar
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import (
    SITE_NAME,
    FEATURE_CHAT_HISTORY,
    FEATURE_FILE_UPLOAD,
    CHAT_RATE_LIMIT_PER_MINUTE,
    UPLOAD_RATE_LIMIT_PER_MINUTE,
    API_TOKEN,
    LOG_FORMAT,
)
from rate_limiter import FixedWindowRateLimiter

# 引入我们刚才拆分出来的路由模块
from routers import chat, upload, knowledge

logger = logging.getLogger("onebase.backend")

# 请求 ID 上下文变量，贯穿单次请求的所有日志
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")

# 结构化日志配置
if LOG_FORMAT == "json":
    import json as _json

    class _JsonFormatter(logging.Formatter):
        def format(self, record):
            return _json.dumps(
                {
                    "ts": self.formatTime(record),
                    "level": record.levelname,
                    "logger": record.name,
                    "msg": record.getMessage(),
                    "rid": request_id_var.get("-"),
                },
                ensure_ascii=False,
            )

    _handler = logging.StreamHandler()
    _handler.setFormatter(_JsonFormatter())
    logging.getLogger("onebase.backend").handlers = [_handler]
    logging.getLogger("onebase.backend").setLevel(logging.INFO)

app = FastAPI(title=f"{SITE_NAME} API")
rate_limiter = FixedWindowRateLimiter()

# 🌟 [3-2] CORS 安全配置：通过环境变量允许用户自定义允许的前端域名
# 默认 * 允许所有（本地开发友好），生产环境建议在 .env 中设置 CORS_ORIGINS
_cors_origins_raw = os.getenv("CORS_ORIGINS", "*")
_cors_origins = (
    [o.strip() for o in _cors_origins_raw.split(",")]
    if _cors_origins_raw != "*"
    else ["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=(_cors_origins != ["*"]),  # 仅在明确指定域名时才允许携带凭据
    allow_methods=["*"],
    allow_headers=["*"],
)


# 🆔 请求 ID 中间件：为每个请求生成唯一标识，便于日志追踪
@app.middleware("http")
async def apply_request_id(request: Request, call_next):
    rid = request.headers.get("x-request-id", uuid.uuid4().hex[:12])
    request_id_var.set(rid)
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Request-ID"] = rid
    logger.info(
        "%s %s %d %.0fms [rid=%s]",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
        rid,
    )
    return response


# 🔐 Token 鉴权中间件：当 API_TOKEN 被设置时，对所有 /api/* 端点（除 health）进行校验
_AUTH_WHITELIST = {"/api/health"}


@app.middleware("http")
async def apply_auth(request, call_next):
    path = request.url.path
    if API_TOKEN and path.startswith("/api/") and path not in _AUTH_WHITELIST:
        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer ") or auth_header[7:] != API_TOKEN:
            client_ip = request.client.host if request.client else "unknown"
            logger.warning(
                "鉴权失败: %s %s 来源=%s [rid=%s]",
                request.method,
                path,
                client_ip,
                request_id_var.get("-"),
            )
            return JSONResponse(
                status_code=401,
                content={"detail": "未授权访问，请提供有效的 API Token"},
                headers={"WWW-Authenticate": "Bearer"},
            )
    return await call_next(request)


@app.middleware("http")
async def apply_rate_limit(request, call_next):
    path = request.url.path

    if path == "/api/chat":
        client_host = request.client.host if request.client else "unknown"
        allowed, retry_after = rate_limiter.allow(
            bucket="chat",
            subject=client_host,
            limit=CHAT_RATE_LIMIT_PER_MINUTE,
            window_sec=60,
        )
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "请求过于频繁，请稍后再试",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

    if path == "/api/upload":
        client_host = request.client.host if request.client else "unknown"
        allowed, retry_after = rate_limiter.allow(
            bucket="upload",
            subject=client_host,
            limit=UPLOAD_RATE_LIMIT_PER_MINUTE,
            window_sec=60,
        )
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "上传请求过于频繁，请稍后再试",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

    return await call_next(request)


@app.get("/api/health")
async def health_check():
    # 🌟 [Step2] 返回 feature flags，供前端根据开关状态条件渲染 UI
    return {
        "status": "ok",
        "site_name": SITE_NAME,
        "features": {
            "chat_history": FEATURE_CHAT_HISTORY,
            "file_upload": FEATURE_FILE_UPLOAD,
        },
    }


# 🚀 将子路由注册到主应用中，并统一加上 /api 前缀
app.include_router(chat.router, prefix="/api")
app.include_router(knowledge.router, prefix="/api")

# 🌟 [Step2] 只有开启 file_upload 时才注册上传路由
if FEATURE_FILE_UPLOAD:
    app.include_router(upload.router, prefix="/api")

# --- 增强版静态页面托管 ---
if os.path.exists("static"):
    # 1. 定义一个自定义类，重写静态文件返回逻辑
    class CachedStaticFiles(StaticFiles):
        async def get_response(self, path: str, scope):
            response = await super().get_response(path, scope)
            # 🌟 针对 assets 目录下的构建产物 (带 Hash 的文件) 开启强缓存
            # max-age=31536000 代表一年，immutable 告诉浏览器内容永不改变
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
            return response

    # 2. 挂载 /assets 目录 (使用我们自定义的缓存类)
    app.mount("/assets", CachedStaticFiles(directory="static/assets"), name="assets")

    # 3. 根路径 index.html 严禁强缓存！
    # 因为它是入口，如果它被缓存，你更新代码后用户就看不到新版本了
    @app.get("/{catchall:path}", include_in_schema=False)
    async def serve_spa(catchall: str):
        file_path = os.path.join("static", catchall)
        if os.path.isfile(file_path):
            return FileResponse(file_path)

        # 🌟 显式为 index.html 设置 no-cache，确保用户每次都能拿到最新的入口
        return FileResponse(
            "static/index.html",
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
        )
