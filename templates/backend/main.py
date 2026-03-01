import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import SITE_NAME, FEATURE_CHAT_HISTORY, FEATURE_FILE_UPLOAD

# 引入我们刚才拆分出来的路由模块
from routers import chat, upload, knowledge

app = FastAPI(title=f"{SITE_NAME} API")

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
