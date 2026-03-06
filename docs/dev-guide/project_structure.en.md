# Project Structure

Complete file organization and module responsibilities for the OneBase project.

---

## Repository Structure

```
onebase-repo/
├── pyproject.toml          # Package metadata, dependencies, entry points
├── MANIFEST.in             # Extra files for sdist packaging
├── LICENSE                 # MIT License
├── README.md               # Project description
├── mkdocs.yml              # Documentation site config
├── onebase.yml             # Example site config (for development)
├── .env                    # Environment variables (not in version control)
│
├── onebase/                # 🐍 CLI core package
├── templates/              # 🐳 Docker runtime templates
├── docs/                   # 📖 MkDocs documentation source
├── base/                   # 📚 Example knowledge base directory
└── overrides/              # 🎨 MkDocs theme overrides
```

---

## onebase/ — CLI Core Package

All source code for the CLI tool. After installing via `pip install onebase-ai`, users invoke the `onebase` command.

```
onebase/
├── __init__.py         # Package init, version export
├── cli.py              # Typer CLI entry: init / build / serve / stop / get-deps
├── config.py           # Pydantic data models (OneBaseConfig)
├── builder.py          # Knowledge base directory scanning & structure parsing
├── chunker.py          # Document chunking (RecursiveCharacterTextSplitter)
├── indexer.py          # Vector indexing (PGVector writes)
├── factory.py          # Model factory (13 reasoning + 10 embedding providers)
├── docker_runner.py    # Docker Compose orchestration & lifecycle management
├── deps_manager.py     # Dynamic dependency detection (provider → PyPI mapping)
├── db.py               # Single source of truth for database connection strings
├── logger.py           # Rich logging & global Console instance
├── i18n.py             # Runtime i18n translation function _()
├── locales/            # Language pack directory
│   └── zh.py           # Chinese translations
└── requirements.txt    # Core runtime dependencies
```

### Module Dependency Graph

```
cli.py
 ├── config.py          ← Load & validate onebase.yml
 ├── builder.py         ← Scan knowledge base directory
 ├── chunker.py         ← Document chunking
 ├── indexer.py         ← Vector indexing
 │    ├── factory.py    ← Create Embedding model instances
 │    └── db.py         ← Build database connection strings
 ├── docker_runner.py   ← Docker Compose orchestration
 │    └── db.py         ← Get database credentials
 ├── deps_manager.py    ← Detect provider dependencies
 ├── logger.py          ← Global logging
 └── i18n.py            ← Translation function
```

### Key File Details

| File               | Responsibility                                                                                                                             |
| :----------------- | :----------------------------------------------------------------------------------------------------------------------------------------- |
| `cli.py`           | Typer app entry point, registers 5 subcommands, handles global options (`--lang` / `--verbose` / `--quiet`)                                |
| `config.py`        | 6 Pydantic BaseModel classes, loads `onebase.yml` with type + constraint validation                                                        |
| `factory.py`       | `ModelFactory` static class, dynamically imports and instantiates LangChain models by provider. Includes `_docker_rewrite()` network logic |
| `docker_runner.py` | `DockerRunner` class, generates `docker-compose.yml`, copies templates, manages container lifecycle                                        |
| `db.py`            | `get_db_credentials()` and `build_db_url()`, eliminates scattered database credential handling                                             |
| `builder.py`       | `KnowledgeBuilder` class, supports `struct: default` (auto-scan) and manual dictionary modes                                               |
| `chunker.py`       | `DocumentProcessor` class, LangChain `RecursiveCharacterTextSplitter` chunking with breadcrumb metadata injection                          |

---

## templates/ — Docker Runtime Templates

During `onebase build` / `onebase serve`, the CLI copies files from this directory to `.onebase/` and builds Docker images.

```
templates/
├── backend/                # FastAPI backend application
│   ├── main.py             # FastAPI entry, CORS, auth, route registration, SPA hosting
│   ├── config.py           # Environment variable reader (DATABASE_URL, providers, flags, API_TOKEN)
│   ├── database.py         # SQLAlchemy models (chat_messages, chat_session_meta)
│   ├── schemas.py          # Pydantic request/response models (with input constraints)
│   ├── deps.py             # Model / vector store singleton management (thread-safe)
│   ├── Dockerfile          # Backend container build file
│   ├── requirements.txt    # Backend Python deps (30 packages, all version-locked)
│   ├── routers/            # Route modules
│   │   ├── chat.py         # /api/chat (SSE streaming), /api/sessions, /api/history
│   │   ├── knowledge.py    # /api/tree, /api/file/{path}
│   │   └── upload.py       # /api/upload (file upload + real-time vectorization)
│   └── engine/             # Reserved engine extension directory
│   └── vector_store/       # Reserved vector store extension directory
│
├── compose/                # Docker Compose templates (reserved)
│   └── docker-compose.base.yml
│
└── frontend/               # Vue 3 frontend SPA
    ├── index.html          # HTML entry
    ├── package.json        # npm dependencies
    ├── vite.config.js      # Vite build config
    ├── dist/               # Build output (distributed with package)
    ├── public/             # Static assets
    └── src/                # Source code
        ├── App.vue         # Root component (layout, init, Feature Flag reading)
        ├── main.js         # Vue app mount
        ├── style.css       # Global styles + Tailwind CSS 4 entry
        ├── assets/         # SVG logos etc.
        ├── components/     # UI components
        │   ├── Sidebar.vue     # Sidebar (knowledge tree + session list dual tabs)
        │   ├── ChatArea.vue    # Chat area (messages, input, copy/download buttons)
        │   ├── ChatList.vue    # Session list (create, rename, delete)
        │   ├── FilePreview.vue # Document preview panel (MD render / PDF text)
        │   └── TreeNode.vue    # Recursive directory tree node
        └── composables/    # Composition functions
            ├── useChat.js  # Chat logic (SSE parsing, session management)
            └── useAuth.js  # API auth (token management, apiFetch wrapper)
```

---

## tests/ — Test Suite

The `tests/` directory contains all unit tests, using the pytest framework:

```
tests/
├── test_config.py          # OneBaseConfig loading / validation
├── test_factory.py         # ModelFactory provider validation
├── test_builder.py         # KnowledgeBuilder directory scanning / parsing
├── test_chunker.py         # DocumentProcessor chunking logic
├── test_rate_limiter.py    # FixedWindowRateLimiter local mode
├── test_schemas.py         # Pydantic model constraints (role / content / session_id / title)
└── test_auth.py            # API Token auth middleware (FastAPI TestClient)
```

To run:

```bash
pip install -e ".[test]"
pytest -v
```

See the [Testing Guide](../about/contributing.md#testing) for details.

---

## Runtime Generated Directory

`onebase init` and `onebase build` generate the following structure in the user's project directory:

```
my-ai-site/                 # User project root
├── onebase.yml             # Site configuration
├── .env                    # Environment variables
├── requirements.txt        # Dynamic dependencies
├── base/                   # Knowledge base documents
│   └── overview.md
└── .onebase/               # Runtime cache (gitignored)
    ├── docker-compose.yml  # Generated Compose file
    └── backend/            # Backend build context copy
        ├── main.py
        ├── factory.py      # Copied from onebase package
        ├── static/         # Frontend dist copy
        └── ...
```

---

## Related Documentation

- [Backend Implementation](backend.md) — FastAPI architecture and routing
- [Frontend Implementation](frontend.md) — Vue 3 components and composables
- [API Reference](api.md) — All HTTP endpoint documentation
