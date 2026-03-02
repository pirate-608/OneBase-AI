# Database Design

OneBase uses PostgreSQL + pgvector extension, handling both vector retrieval and business data.

---

## Architecture Overview

```
PostgreSQL (pgvector/pgvector:pg16)
│
├── langchain_pg_collection    # PGVector collection registry
├── langchain_pg_embedding     # Vector data table (document chunks + embeddings)
├── chat_messages              # Chat message history
└── chat_session_meta          # Session metadata
```

OneBase has two sets of tables:

1. **PGVector-managed tables** — Automatically created and maintained by LangChain PGVector, storing document vectors
2. **Business tables** — Defined by SQLAlchemy ORM, storing chat history and session information

---

## Vector Storage Tables

Managed automatically by the `PGVector` class from the `langchain-postgres` package. OneBase does not directly manipulate their DDL.

### langchain_pg_collection

Collection registry table. Each OneBase site corresponds to one record.

| Column      | Type    | Description                                                  |
| :---------- | :------ | :----------------------------------------------------------- |
| `uuid`      | UUID    | Primary key                                                  |
| `name`      | VARCHAR | Collection name (from `site_name`: spaces → `_`, lowercased) |
| `cmetadata` | JSONB   | Collection-level metadata                                    |

### langchain_pg_embedding

Vector embedding table for document chunks — the core data source for RAG retrieval.

| Column          | Type    | Description                                     |
| :-------------- | :------ | :---------------------------------------------- |
| `id`            | VARCHAR | Primary key                                     |
| `collection_id` | UUID    | Foreign key → `langchain_pg_collection.uuid`    |
| `embedding`     | VECTOR  | pgvector column, dimensions determined by model |
| `document`      | TEXT    | Original text chunk content                     |
| `cmetadata`     | JSONB   | Chunk metadata (see below)                      |

**cmetadata field structure:**

```json
{
  "title": "overview",
  "breadcrumbs": "section1 > overview",
  "source_file": "overview.md"
}
```

- `title` — Document title (filename without extension)
- `breadcrumbs` — Navigation path (from YAML struct or auto-scan)
- `source_file` — Original filename

Files uploaded via the frontend have breadcrumbs formatted as `User Upload > filename.pdf`.

---

## Business Tables

Defined by SQLAlchemy declarative models in `templates/backend/database.py`.

### chat_messages

Chat message persistence table. Each user question and AI reply is stored as a separate row.

```python
class ChatMessageDB(Base):
    __tablename__ = "chat_messages"

    id         = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    role       = Column(String, nullable=False)    # 'user' | 'assistant'
    content    = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

| Column       | Type        | Index | Description                             |
| :----------- | :---------- | :---: | :-------------------------------------- |
| `id`         | INTEGER     |  PK   | Auto-increment primary key              |
| `session_id` | VARCHAR     |   ✅   | Session identifier (frontend-generated) |
| `role`       | VARCHAR     |   —   | `user` or `assistant`                   |
| `content`    | TEXT        |   —   | Message body                            |
| `created_at` | TIMESTAMPTZ |   —   | Server-side auto-generated timestamp    |

### chat_session_meta

Session metadata table, storing user-defined titles.

```python
class ChatSessionMeta(Base):
    __tablename__ = "chat_session_meta"

    session_id = Column(String, primary_key=True)
    title      = Column(String, nullable=True)
```

| Column       | Type    | Description                                                         |
| :----------- | :------ | :------------------------------------------------------------------ |
| `session_id` | VARCHAR | Primary key, relates to `chat_messages.session_id`                  |
| `title`      | VARCHAR | User-defined title (NULL → frontend uses first 15 chars of message) |

---

## Connection Management

### CLI Side (onebase package)

`onebase/db.py` provides centralized connection string building:

```python
# Credential reading
get_db_credentials() → dict  # Reads POSTGRES_* from .env

# Connection string
build_db_url()                          # CLI connects to host
build_db_url(host_override="db")        # Docker internal network
```

Connection format: `postgresql+psycopg://user:pass@host:port/dbname`

### Backend Side (inside container)

`templates/backend/config.py` reads directly from the `DATABASE_URL` environment variable, injected by `docker_runner.py`.

`templates/backend/database.py` implements lazy initialization + retry:

```python
def _init_db(max_retries=10, retry_interval=2.0):
    # Retry loop to handle PG container startup timing
    for attempt in range(1, max_retries + 1):
        try:
            _engine = create_engine(DB_URL)
            with _engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            Base.metadata.create_all(bind=_engine)  # Auto-create tables
            return
        except Exception:
            time.sleep(retry_interval)
```

---

## Data Flow

```
User documents (base/)
    ↓ builder.py — Scan & parse
    ↓ chunker.py — Chunk + metadata injection
    ↓ indexer.py — Call Embedding API
    ↓
langchain_pg_embedding (vector write)
    ↓
Similarity search ← /api/chat request
    ↓
chat_messages (conversation persistence)
```

---

## Feature Flag Impact on Database

| Flag                  | Impact                                                                              |
| :-------------------- | :---------------------------------------------------------------------------------- |
| `chat_history: false` | `chat_messages` and `chat_session_meta` tables are still created but not written to |
| `file_upload: false`  | Upload route is disabled; `langchain_pg_embedding` won't have `User Upload` records |

---

## Data Cleanup

```bash
# Keep containers, clear vector data (requires rebuild)
docker exec -it <db_container> psql -U onebase -d onebase_db \
  -c "TRUNCATE langchain_pg_embedding, langchain_pg_collection CASCADE;"

# Keep containers, clear chat history
docker exec -it <db_container> psql -U onebase -d onebase_db \
  -c "TRUNCATE chat_messages, chat_session_meta;"

# Complete destruction (remove volumes)
onebase stop -v
```

---

## Related Documentation

- [Database Configuration](../user-guide/config/database.md) — Credentials and environment variables
- [Security Configuration](../user-guide/config/security.md) — Password generation and port exposure
- [Project Structure](project_structure.md) — File location reference
