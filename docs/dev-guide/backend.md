# 后端实现

OneBase 后端是一个 FastAPI 应用，运行在 Docker 容器内，提供 RAG 对话、知识库浏览和文件上传服务。

---

## 技术栈

| 技术       | 用途                |
| :--------- | :------------------ |
| FastAPI    | Web 框架            |
| SQLAlchemy | ORM + 数据库管理    |
| LangChain  | LLM 调用 + 向量检索 |
| PGVector   | 向量存储            |
| Uvicorn    | ASGI 服务器         |

---

## 应用架构

```
main.py                      # FastAPI 入口
├── config.py                # 环境变量集中读取
├── database.py              # SQLAlchemy 模型 + 连接管理
├── schemas.py               # Pydantic 请求模型
├── factory.py               # 模型工厂（从 CLI 包拷贝）
└── routers/
    ├── chat.py              # 对话 + 会话管理
    ├── knowledge.py         # 目录树 + 文档预览
    └── upload.py            # 文件上传 + 向量化
```

---

## 启动流程

### 1. 环境变量注入

`docker_runner.py` 将以下变量注入容器：

```
DATABASE_URL           ← build_db_url(host_override="db")
SITE_NAME              ← onebase.yml → site_name
REASONING_PROVIDER     ← engine.reasoning.provider
REASONING_MODEL        ← engine.reasoning.model
EMBEDDING_PROVIDER     ← engine.embedding.provider
EMBEDDING_MODEL        ← engine.embedding.model
FEATURE_CHAT_HISTORY   ← features.chat_history
FEATURE_FILE_UPLOAD    ← features.file_upload
RUNNING_IN_DOCKER      ← "true"
```

加上 `.env` 中的 API 密钥（通过 `env_file` 方式注入）。

### 2. 配置校验

`config.py` 在模块加载时读取环境变量，`DATABASE_URL` 缺失则立即 `sys.exit(1)`：

```python
DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    sys.exit(1)
```

### 3. CORS 中间件

```python
_cors_origins_raw = os.getenv("CORS_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=(_cors_origins != ["*"]),
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- 默认 `*` 允许所有来源（本地开发）
- 指定域名时开启 `allow_credentials`

### 4. 路由注册

```python
app.include_router(chat.router, prefix="/api")
app.include_router(knowledge.router, prefix="/api")

if FEATURE_FILE_UPLOAD:
    app.include_router(upload.router, prefix="/api")
```

`upload` 路由在 `file_upload: false` 时不注册，完全移除端点。

### 5. 数据库懒初始化

首次 API 请求触发 `_init_db()`，带重试机制应对容器启动时序：

- 最多重试 10 次，间隔 2 秒
- 连接成功后自动执行 `Base.metadata.create_all()` 建表

---

## 路由模块详解

### chat.py — 对话路由

**6 个端点：** 

| 端点                       | 说明          |
| :------------------------- | :------------ |
| `POST /api/chat`           | 流式 RAG 对话 |
| `GET /api/sessions`        | 会话列表      |
| `PUT /api/sessions/{id}`   | 重命名会话    |
| `GET /api/history/{id}`    | 获取消息历史  |
| `DELETE /api/history/{id}` | 删除会话      |

**RAG 流式对话核心流程：**

```python
# 1. 持久化用户消息
if FEATURE_CHAT_HISTORY:
    db.add(ChatMessageDB(session_id=..., role="user", content=...))

# 2. 上下文锚点拼接
search_query = f"背景语境: {last_ai_reply[:200]}\n用户问题: {user_query}"

# 3. 向量检索（top 4）
retrieved_docs = vector_store.similarity_search(search_query, k=4)

# 4. System Prompt 构建
system_prompt = f"""你是 "{SITE_NAME}" 的专属 AI 助手。
【参考资料】
{context_text}
"""

# 5. SSE 流式返回
async def generate_stream():
    async for chunk in llm.astream(messages):
        yield f"data: {json.dumps({'content': chunk.content})}\n\n"
    yield "data: [DONE]\n\n"

# 6. finally: 独立 Session 保存 AI 回复
```

**DB Session 生命周期：** 流式生成器的 `finally` 块中使用独立的 `_SessionLocal()` 保存 AI 回复，因为 FastAPI 的 `Depends(get_db)` 注入的 Session 可能在流结束前已被关闭。

### knowledge.py — 知识库路由

| 端点                   | 说明                        |
| :--------------------- | :-------------------------- |
| `GET /api/tree`        | 返回目录树（JSON 嵌套结构） |
| `GET /api/file/{path}` | 返回文档内容                |

**目录树构建：**

- `struct: default` → 递归扫描 `base/` 物理目录
- `struct: {dict}` → 按字典结构生成树

**文档内容获取：**

- MD/TXT：智能编码探测（先 UTF-8，失败后 chardet 回退）
- PDF：`PyPDFLoader` 提取文本，按页分隔
- 路径遍历防护：`Path.resolve().is_relative_to(Path("base").resolve())`

**同步端点设计：** `knowledge.py` 的端点使用 `def` 而非 `async def`，FastAPI 自动将其放入线程池执行，避免文件 I/O 阻塞事件循环。

### upload.py — 上传路由

| 端点               | 说明                     |
| :----------------- | :----------------------- |
| `POST /api/upload` | 上传文件，切块向量化写入 |

**安全措施：**

- 文件大小限制：20 MB
- 格式白名单：`.pdf`、`.txt`、`.md`
- Feature Flag 门控：`FEATURE_FILE_UPLOAD` 为 false 时返回 403
- 错误信息脱敏：500 错误只返回 `"文件处理失败"`，详情写入日志

---

## 模型工厂（factory.py）

`ModelFactory` 静态类在 CLI 和后端中共用（CLI 打包时拷贝到容器内）。

### 推理模型

`ModelFactory.get_reasoning_model(provider, model_name)` 支持 13 个 provider：

| provider    | LangChain 类             | 密钥环境变量        |
| :---------- | :----------------------- | :------------------ |
| `openai`    | `ChatOpenAI`             | `OPENAI_API_KEY`    |
| `ollama`    | `ChatOllama`             | —                   |
| `dashscope` | `ChatTongyi`             | `DASHSCOPE_API_KEY` |
| `zhipu`     | `ChatZhipuAI`            | `ZHIPU_API_KEY`     |
| `anthropic` | `ChatAnthropic`          | `ANTHROPIC_API_KEY` |
| `google`    | `ChatGoogleGenerativeAI` | `GOOGLE_API_KEY`    |
| `deepseek`  | `ChatDeepSeek`           | `DEEPSEEK_API_KEY`  |
| `groq`      | `ChatGroq`               | `GROQ_API_KEY`      |
| ...         | ...                      | ...                 |

### 嵌入模型

`ModelFactory.get_embedding_model(provider, model_name)` 支持 10 个 provider。

### Docker 网络重写

```python
def _docker_rewrite(url):
    if os.getenv("RUNNING_IN_DOCKER"):
        return re.sub(r"localhost|127\.0\.0\.1", "host.docker.internal", url)
    return url
```

当 `RUNNING_IN_DOCKER=true` 时，自动将 `localhost` 替换为 `host.docker.internal`，确保容器内能访问宿主机上的 Ollama 等服务。

---

## 静态文件托管

后端同时担任前端静态文件服务器：

```python
# 构建产物强缓存（文件名含 hash）
app.mount("/assets", CachedStaticFiles(directory="static/assets"))
# Cache-Control: public, max-age=31536000, immutable

# SPA 入口不缓存
@app.get("/{catchall:path}")
async def serve_spa(catchall):
    return FileResponse("static/index.html",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"})
```

**缓存策略：**

| 路径         | 策略              | 原因                                     |
| :----------- | :---------------- | :--------------------------------------- |
| `/assets/*`  | `immutable`, 1 年 | 文件名含 hash，内容变化则 URL 变化       |
| `index.html` | `no-cache`        | 入口文件必须实时获取，否则用户看不到更新 |

---

## Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`pip install --upgrade pip` 解决了 pip 旧版本的 `ResolutionTooDeep` 错误。`requirements.txt` 中所有 30 个依赖均锁定版本范围。

---

## 相关文档

- [API 文档](api.md) — 全部接口的请求/响应规范
- [前端实现](frontend.md) — Vue 组件如何消费 API
- [数据库设计](database_design.md) — 表结构定义
- [目录结构](project_structure.md) — 后端文件位置
