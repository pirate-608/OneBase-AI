import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import SITE_NAME
# 引入我们刚才拆分出来的路由模块
from routers import chat, upload, knowledge

app = FastAPI(title=f"{SITE_NAME} API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "site_name": SITE_NAME}

# 🚀 将子路由注册到主应用中，并统一加上 /api 前缀
app.include_router(chat.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(knowledge.router, prefix="/api")

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
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )