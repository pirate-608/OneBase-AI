# Basic Commands

OneBase CLI provides 5 core commands covering the full project lifecycle from initialization to shutdown.

---

## Command Overview

```bash
onebase [global options] <command> [command options]
```

| Command    | Description                     | Prerequisites                      |
| :--------- | :------------------------------ | :--------------------------------- |
| `init`     | Initialize project structure    | None                               |
| `get-deps` | Detect and output dependencies  | `onebase.yml`                      |
| `build`    | Build the vector knowledge base | `onebase.yml` + documents + Docker |
| `serve`    | Start the full service stack    | `onebase.yml` + Docker             |
| `stop`     | Stop and remove containers      | Running services                   |

---

## init — Initialize Project

Create a new OneBase project with all necessary configuration files.

```bash
onebase init
onebase init --force   # Overwrite existing files
```

Generated files and directories:

| File/Directory     | Content                                        |
| :----------------- | :--------------------------------------------- |
| `onebase.yml`      | Site config (engine, database, knowledge base) |
| `.env`             | Database credentials + API key template        |
| `base/`            | Knowledge base directory with `overview.md`    |
| `.onebase/`        | Runtime cache directory                        |
| `requirements.txt` | Dependency list template                       |

### Typical Workflow

```bash
mkdir my-ai-site && cd my-ai-site
onebase init
# Edit onebase.yml and .env
onebase get-deps > requirements.txt
pip install -r requirements.txt
```

!!! tip "Security Design"
    `POSTGRES_PASSWORD` in `.env` is auto-generated using `secrets.token_urlsafe(16)` — a 128-bit cryptographically secure random password.

---

## get-deps — Detect Dependencies

Automatically calculates required Python packages based on the provider and features configured in `onebase.yml`.

```bash
onebase get-deps                     # Output to terminal
onebase get-deps > requirements.txt  # Redirect to file
```

Example output:

```
langchain-ollama>=0.2.0
langchain-community>=0.3.0
psycopg[binary]>=3.1
```

!!! info "Why is this step needed?"
    OneBase core only includes essential logic. Inference SDKs (e.g., `langchain-openai`, `langchain-ollama`) are installed on demand. `get-deps` precisely outputs dependencies based on your chosen providers, avoiding unnecessary packages.

---

## build — Build Knowledge Base

Parse documents, generate vector chunks, and write to the database. This is the critical step from raw documents to searchable state.

```bash
onebase build
onebase build --with-ollama
onebase build --with-ollama --use-gpu
```

### Execution Flow

```
Parse onebase.yml
     ↓
Scan base/ directory (MD/PDF/TXT)
     ↓
Chunk documents (by chunk_size)
     ↓
Start Docker containers (db + optional inference engine)
     ↓
Wait for PostgreSQL ready (up to 30s)
     ↓
Vectorize & write to pgvector
```

### Use Cases

| Scenario                  | Command                           |
| :------------------------ | :-------------------------------- |
| Ollama on host            | `onebase build`                   |
| Containerized Ollama      | `onebase build --with-ollama`     |
| GPU-accelerated embedding | `onebase build --with-ollama -g`  |
| Using Xinference          | `onebase build --with-xinference` |
| Using vLLM                | `onebase build --with-vllm`       |

!!! warning "Inference Engine Mutual Exclusion"
    `--with-ollama`, `--with-xinference`, and `--with-vllm` are mutually exclusive — only one can be specified at a time.

!!! note "First use with containerized models"
    If model weights haven't been downloaded in the container, vectorization may fail. Start the container first with `onebase serve --with-ollama -d` and manually pull models before running `build`.

---

## serve — Start Services

Start the full stack: backend API + database + frontend UI + optional inference engine.

```bash
onebase serve              # Foreground
onebase serve -d           # Background (detached)
onebase serve -d -p 3000   # Background, port 3000
onebase serve --with-ollama -d   # With Ollama container
```

### Startup Flow

```
Parse onebase.yml
     ↓
Try pulling pre-built image (15s timeout)
  ├─ Success → Use remote image
  └─ Failure → Build image locally
     ↓
Generate docker-compose.yml
     ↓
docker compose up [-d] [--build]
     ↓
Output access URL and status panel
```

### Post-Startup Output

Background mode (`-d`) displays a status panel on success:

```
╭─── Status: Online ───╮
│ 🎉 OneBase is running!                           │
│                                                    │
│ 🌐 URL: http://localhost:8000                      │
│ 🛑 Stop: run onebase stop                          │
╰────────────────────────────────────────────────────╯
```

Foreground mode outputs live container logs. Press `Ctrl+C` to stop.

---

## stop — Stop Services

Stop all running OneBase containers and clean up networks.

```bash
onebase stop       # Stop containers, keep data
onebase stop -v    # Stop and remove data volumes
```

!!! danger "`-v` is irreversible"
    Using `--volumes` permanently deletes:

    - PostgreSQL database (all vector data)
    - Local model cache (Ollama / Xinference / vLLM weights)

    After deletion, you'll need to `build` again and re-download containerized models.

---

## Global Options

These options go **before** any command and affect global behavior.

```bash
onebase --version          # Show version
onebase --lang zh build    # Chinese output
onebase --verbose serve -d # Debug mode
onebase --quiet build      # Quiet mode (errors only)
```

| Option      | Short | Description                           |
| :---------- | :---- | :------------------------------------ |
| `--version` | `-V`  | Show version and exit                 |
| `--lang`    | `-l`  | Output language: `en` (default), `zh` |
| `--verbose` | `-v`  | Debug mode with verbose logging       |
| `--quiet`   | `-q`  | Quiet mode, errors only               |
| `--help`    | `-h`  | Show help                             |

!!! tip "Persistent Language Setting"
    Set the `ONEBASE_LANG=zh` environment variable to avoid typing `--lang zh` every time.

---

## Related Documentation

- [Arguments Reference](args.md) — Complete option details and examples
- [Local Deployment](../deploy/cloud_deploy.en.md) — End-to-end deployment guide
- [Preset Configurations](../config/preset_config.en.md) — Common scenario templates
