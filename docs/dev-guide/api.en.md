# API Reference

The OneBase backend is built on FastAPI. All endpoints use the `/api` prefix. This page documents all HTTP endpoint request/response specifications.

---

## Overview

| Method | Path                         | Description                  | Feature Flag   |
| :----- | :--------------------------- | :--------------------------- | :------------- |
| GET    | `/api/health`                | Health check + Feature Flags | —              |
| POST   | `/api/chat`                  | Streaming chat (SSE)         | —              |
| GET    | `/api/sessions`              | List sessions                | `chat_history` |
| PUT    | `/api/sessions/{session_id}` | Rename session               | `chat_history` |
| GET    | `/api/history/{session_id}`  | Get session history          | `chat_history` |
| DELETE | `/api/history/{session_id}`  | Delete session               | `chat_history` |
| GET    | `/api/tree`                  | Knowledge base tree          | —              |
| GET    | `/api/file/{file_path}`      | Get document content         | —              |
| POST   | `/api/upload`                | Upload and vectorize         | `file_upload`  |

---

## Health Check

### GET /api/health

Returns service status and Feature Flags for frontend initialization.

**Response 200:**

```json
{
  "status": "ok",
  "site_name": "My AI Assistant",
  "features": {
    "chat_history": true,
    "file_upload": true
  }
}
```

---

## Chat

### POST /api/chat

Knowledge-base-powered streaming chat using Server-Sent Events (SSE).

**Request body:**

```json
{
  "session_id": "session_abc123",
  "messages": [
    { "role": "user", "content": "What is OneBase?" }
  ],
  "stream": true
}
```

| Field                | Type   | Required | Description                             |
| :------------------- | :----- | :------: | :-------------------------------------- |
| `session_id`         | string |    —     | Session ID, default `"default-session"` |
| `messages`           | array  |    ✅     | Message list, last one is current input |
| `messages[].role`    | string |    ✅     | `"user"` or `"assistant"`               |
| `messages[].content` | string |    ✅     | Message body                            |
| `stream`             | bool   |    —     | Stream response, default `true`         |

**Response** (`text/event-stream`):

```
data: {"content": "OneBase is"}

data: {"content": " a RAG framework"}

data: [DONE]
```

Each `data:` line contains a JSON object with an incremental `content` field. `[DONE]` marks the end of the stream.

**Error event:**

```
data: {"error": "Model call failed: Connection refused"}
```

**Internal flow:**

1. Save user message to `chat_messages` (when `chat_history` is enabled)
2. Build context anchor (last AI reply's first 200 chars + current question)
3. Vector similarity search (`similarity_search`, top 4 chunks)
4. Build System Prompt (inject retrieved results + breadcrumb sources)
5. Stream LLM call (`llm.astream()`)
6. After stream ends, save AI reply to `chat_messages`

---

## Session Management

### GET /api/sessions

Get all historical sessions, sorted by last active time descending.

**Response 200:**

```json
[
  {
    "id": "session_abc123",
    "title": "What is OneBase?...",
    "created_at": "2026-03-02T10:30:00+08:00"
  }
]
```

`title` uses the user-defined title (`chat_session_meta`) if available, otherwise the first 15 characters of the first user message.

---

### PUT /api/sessions/{session_id}

Rename a session.

**Request body:**

```json
{
  "title": "Discussion about OneBase"
}
```

**Response 200:**

```json
{
  "status": "success",
  "title": "Discussion about OneBase"
}
```

---

### GET /api/history/{session_id}

Get complete message history for a session, sorted by time ascending.

**Response 200:**

```json
[
  { "role": "user", "content": "What is OneBase?" },
  { "role": "assistant", "content": "OneBase is a..." }
]
```

---

### DELETE /api/history/{session_id}

Delete all messages for a session.

**Response 200:**

```json
{ "status": "success" }
```

---

## Knowledge Base

### GET /api/tree

Get the knowledge base directory tree structure. Depends on `struct` in `onebase.yml`:

- `struct: default` → Auto-scan `base/` directory
- `struct: {dict}` → Return manually configured structure

**Response 200:**

```json
[
  {
    "title": "section1",
    "type": "folder",
    "isOpen": false,
    "children": [
      { "title": "overview", "type": "file", "path": "section1/overview.md" }
    ]
  },
  { "title": "faq", "type": "file", "path": "faq.txt" }
]
```

| Field      | Type   | Description                           |
| :--------- | :----- | :------------------------------------ |
| `title`    | string | Display title                         |
| `type`     | string | `"folder"` or `"file"`                |
| `isOpen`   | bool   | Folder default collapsed state        |
| `children` | array  | Child nodes (folders only)            |
| `path`     | string | Path relative to `base/` (files only) |

---

### GET /api/file/{file_path}

Get document text content. Supports Markdown, TXT, and PDF (text extraction).

**Path parameter:** `file_path` — Path relative to `base/`

**Response 200:**

```json
{ "content": "# Welcome\n\nThis is the overview document..." }
```

**PDF response format:**

```json
{ "content": "**--- Page 1 ---**\n\nPage content...\n\n**--- Page 2 ---**\n\n..." }
```

**Error 403:**

```json
{ "detail": "Directory traversal forbidden" }
```

Path traversal protection: The backend uses `Path.resolve().is_relative_to()` to verify the real path is within `base/`.

---

## File Upload

### POST /api/upload

Upload a document and vectorize it into the knowledge base in real-time. Only available when `file_upload: true`.

**Request:** `multipart/form-data`

| Field  | Type | Description                    |
| :----- | :--- | :----------------------------- |
| `file` | File | Uploaded file (PDF / TXT / MD) |

**Limits:**

- Max file size: 20 MB
- Supported formats: `.pdf`, `.txt`, `.md`

**Response 200:**

```json
{
  "status": "success",
  "filename": "api-reference.pdf",
  "chunks": 42
}
```

**Error responses:**

| Status | Description                               |
| :----- | :---------------------------------------- |
| 400    | Unsupported file format                   |
| 403    | File upload disabled (Feature Flag)       |
| 413    | File exceeds 20 MB limit                  |
| 500    | Server processing failed (details logged) |

**Internal flow:**

1. Validate file format and size
2. Write to temp file → load and parse
3. `RecursiveCharacterTextSplitter` chunking (chunk_size=500, overlap=50)
4. Inject metadata `breadcrumbs: "User Upload > filename"`
5. Call Embedding model for vectorization
6. Write to pgvector

---

## Static Assets

### GET /{catchall}

SPA frontend hosting. The backend serves Vue build output as static files:

- `/assets/*` — Hashed build artifacts with strong caching (`max-age=31536000, immutable`)
- Other paths — Fallback to `index.html` with `no-cache` to ensure users always get the latest entry

---

## Related Documentation

- [Backend Implementation](backend.md) — Route modules and middleware design
- [Frontend Implementation](frontend.md) — How the frontend consumes these APIs
- [Database Design](database_design.md) — Table structure and data flow
