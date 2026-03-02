# Backend Implementation

The OneBase backend is a FastAPI application running inside a Docker container, providing RAG chat, knowledge base browsing, and file upload services.

---

## Tech Stack

| Technology | Purpose                   |
| :--------- | :------------------------ |
| FastAPI    | Web framework             |
| SQLAlchemy | ORM + DB management       |
| LangChain  | LLM calls + vector search |
| PGVector   | Vector storage            |
| Uvicorn    | ASGI server               |

---

## Application Architecture

```
main.py                      # FastAPI entry
├── config.py                # Centralized env var reading
├── database.py              # SQLAlchemy models + connection management
├── schemas.py               # Pydantic request models
├── factory.py               # Model factory (copied from CLI package)
└── routers/
    ├── chat.py              # Chat + session management
    ├── knowledge.py         # Directory tree + document preview
    └── upload.py            # File upload + vectorization
```

---

## Startup Flow

### 1. Environment Variable Injection

`docker_runner.py` injects the following variables into the container:

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

Plus API keys from `.env` (injected via `env_file`).

### 2. Configuration Validation

`config.py` reads environment variables at module load time. Missing `DATABASE_URL` triggers immediate `sys.exit(1)`:

```python
DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    sys.exit(1)
```

### 3. CORS Middleware

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

- Default `*` allows all origins (local development)
- Specified domains enable `allow_credentials`

### 4. Route Registration

```python
app.include_router(chat.router, prefix="/api")
app.include_router(knowledge.router, prefix="/api")

if FEATURE_FILE_UPLOAD:
    app.include_router(upload.router, prefix="/api")
```

The `upload` route is not registered when `file_upload: false`, completely removing the endpoint.

### 5. Lazy Database Initialization

The first API request triggers `_init_db()` with retry logic for container startup timing:

- Up to 10 retries, 2-second intervals
- On success, auto-executes `Base.metadata.create_all()` to create tables

---

## Route Module Details

### chat.py — Chat Routes

**6 endpoints:**

| Endpoint                   | Description         |
| :------------------------- | :------------------ |
| `POST /api/chat`           | Streaming RAG chat  |
| `GET /api/sessions`        | Session list        |
| `PUT /api/sessions/{id}`   | Rename session      |
| `GET /api/history/{id}`    | Get message history |
| `DELETE /api/history/{id}` | Delete session      |

**RAG Streaming Chat Core Flow:**

```python
# 1. Persist user message
if FEATURE_CHAT_HISTORY:
    db.add(ChatMessageDB(session_id=..., role="user", content=...))

# 2. Context anchor construction
search_query = f"Background: {last_ai_reply[:200]}\nUser question: {user_query}"

# 3. Vector search (top 4)
retrieved_docs = vector_store.similarity_search(search_query, k=4)

# 4. System Prompt construction
system_prompt = f"""You are the dedicated AI assistant for "{SITE_NAME}".
【Reference Materials】
{context_text}
"""

# 5. SSE streaming response
async def generate_stream():
    async for chunk in llm.astream(messages):
        yield f"data: {json.dumps({'content': chunk.content})}\n\n"
    yield "data: [DONE]\n\n"

# 6. finally: independent Session saves AI reply
```

**DB Session Lifecycle:** The `finally` block of the streaming generator uses an independent `_SessionLocal()` to save the AI reply, because FastAPI's `Depends(get_db)` injected Session may be closed before the stream ends.

### knowledge.py — Knowledge Base Routes

| Endpoint               | Description                         |
| :--------------------- | :---------------------------------- |
| `GET /api/tree`        | Return directory tree (nested JSON) |
| `GET /api/file/{path}` | Return document content             |

**Directory tree construction:**

- `struct: default` → Recursive scan of `base/` physical directory
- `struct: {dict}` → Generate tree from dictionary structure

**Document content retrieval:**

- MD/TXT: Smart encoding detection (try UTF-8 first, fallback to chardet)
- PDF: `PyPDFLoader` text extraction, page-separated
- Path traversal protection: `Path.resolve().is_relative_to(Path("base").resolve())`

**Synchronous endpoint design:** `knowledge.py` endpoints use `def` instead of `async def`. FastAPI automatically runs them in a thread pool, avoiding file I/O blocking the event loop.

### upload.py — Upload Route

| Endpoint           | Description                      |
| :----------------- | :------------------------------- |
| `POST /api/upload` | Upload file, chunk and vectorize |

**Security measures:**

- File size limit: 20 MB
- Format whitelist: `.pdf`, `.txt`, `.md`
- Feature Flag gate: Returns 403 when `FEATURE_FILE_UPLOAD` is false
- Error message sanitization: 500 errors only return `"File processing failed"`, details logged

---

## Model Factory (factory.py)

The `ModelFactory` static class is shared between CLI and backend (copied to container during CLI packaging).

### Reasoning Models

`ModelFactory.get_reasoning_model(provider, model_name)` supports 13 providers:

| provider    | LangChain Class          | Key Env Var         |
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

### Embedding Models

`ModelFactory.get_embedding_model(provider, model_name)` supports 10 providers.

### Docker Network Rewrite

```python
def _docker_rewrite(url):
    if os.getenv("RUNNING_IN_DOCKER"):
        return re.sub(r"localhost|127\.0\.0\.1", "host.docker.internal", url)
    return url
```

When `RUNNING_IN_DOCKER=true`, automatically replaces `localhost` with `host.docker.internal`, ensuring containers can access host services like Ollama.

---

## Static File Hosting

The backend also serves as the frontend static file server:

```python
# Build artifacts with strong caching (filenames contain hash)
app.mount("/assets", CachedStaticFiles(directory="static/assets"))
# Cache-Control: public, max-age=31536000, immutable

# SPA entry with no caching
@app.get("/{catchall:path}")
async def serve_spa(catchall):
    return FileResponse("static/index.html",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"})
```

**Caching strategy:**

| Path         | Strategy         | Reason                                        |
| :----------- | :--------------- | :-------------------------------------------- |
| `/assets/*`  | `immutable`, 1yr | Filenames contain hash; URL changes on update |
| `index.html` | `no-cache`       | Entry must be fresh for users to see updates  |

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

`pip install --upgrade pip` resolves the `ResolutionTooDeep` error from older pip versions. All 30 dependencies in `requirements.txt` have locked version ranges.

---

## Related Documentation

- [API Reference](api.md) — Full endpoint request/response specs
- [Frontend Implementation](frontend.md) — How Vue components consume APIs
- [Database Design](database_design.md) — Table structure definitions
- [Project Structure](project_structure.md) — Backend file locations
