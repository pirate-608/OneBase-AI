# Security Configuration

OneBase involves API keys, database credentials, and network access control. This page explains each security mechanism and recommended practices.

---

## .env File & Key Management

`onebase init` automatically generates an `.env` file containing a random database password:

```bash title=".env (auto-generated)"
POSTGRES_USER=onebase
POSTGRES_PASSWORD=<random 22-char URL-safe token>   # secrets.token_urlsafe(16)
POSTGRES_DB=onebase_db
```

### Best Practices

| Practice                   | Description                                                          |
| :------------------------- | :------------------------------------------------------------------- |
| **Don't commit `.env`**    | Already excluded in `.gitignore` — verify `.env` never enters VCS    |
| **Separate env passwords** | Use different `POSTGRES_PASSWORD` for dev and production             |
| **Minimize key scope**     | Only fill in keys for providers you actually use; leave others blank |
| **Rotate keys regularly**  | Periodically rotate cloud API keys; restart services after rotation  |

### API Key Storage

All API keys are injected via `.env` — **never put them in `onebase.yml`**:

```bash title=".env"
# Fill in only the provider you're using
OPENAI_API_KEY=sk-...
DASHSCOPE_API_KEY=sk-...
DEEPSEEK_API_KEY=sk-...
```

Keys are passed to Docker containers at runtime via environment variables (`env_file`). They never appear in Docker images or Compose files.

---

## API Token Authentication

OneBase supports Bearer Token authentication via the `API_TOKEN` environment variable for all API requests.

### Enabling

Set in `.env`:

```bash title=".env"
# Once set, all /api/* requests (except /api/health) require this token
API_TOKEN=your-secret-token-here
```

Leave empty or unset to **skip authentication** (default for local development).

### How It Works

The backend registers an auth middleware after CORS and before rate limiting. Every `/api/*` request (except `/api/health`) must include:

```
Authorization: Bearer <API_TOKEN>
```

| Scenario            | Behavior                                                          |
| :------------------ | :---------------------------------------------------------------- |
| Correct token       | Request passes through                                            |
| Missing/wrong token | Returns `401 Unauthorized` with `WWW-Authenticate: Bearer` header |
| `/api/health`       | Always public, no token required                                  |
| `API_TOKEN` unset   | All requests pass through (auth disabled)                         |

### Frontend Integration

The frontend manages tokens automatically via the `useAuth.js` composable:

1. On first page load → check `localStorage` for a cached token
2. If no token → prompt the user to enter one
3. All API requests use `apiFetch()` which automatically attaches the `Authorization` header
4. On `401` response → clear cache and re-prompt

!!! tip "Token delivery"
    `API_TOKEN` is injected into containers via Docker Compose environment variable `${API_TOKEN:-}`. It never appears in images or Compose files.

---

## CORS Policy

The backend controls allowed frontend origins via the `CORS_ORIGINS` environment variable.

### Default Behavior

```python
# templates/backend/main.py
_cors_origins_raw = os.getenv("CORS_ORIGINS", "*")
```

| Scenario     | `CORS_ORIGINS` Value          | Effect                              |
| :----------- | :---------------------------- | :---------------------------------- |
| Local dev    | Omitted (`*`)                 | Allow all origins, no credentials   |
| Production   | `https://yourdomain.com`      | Allow specified domain, credentials |
| Multi-domain | `https://a.com,https://b.com` | Comma-separated, each matched       |

### Configuration

Set in `.env`:

```bash title=".env"
# Production: restrict to actual frontend domain
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

!!! warning "Tighten for production"
    The default `*` is only suitable for local development. When deploying to the public internet, you **must** set `CORS_ORIGINS` to your actual domain, otherwise any website can call your API.

### Credentials Logic

```python
allow_credentials=(_cors_origins != ["*"])
```

- `CORS_ORIGINS=*` → `allow_credentials=False` (browser won't send cookies)
- Specified domain → `allow_credentials=True` (allows Cookie / Authorization headers)

---

## Database Security

### Password Generation

`onebase init` uses Python's `secrets` module to generate passwords:

```python
import secrets
db_password = secrets.token_urlsafe(16)  # 22 chars, cryptographically secure
```

Generated passwords satisfy:

- 128-bit entropy (`token_urlsafe(16)` = 16 bytes = 128 bits)
- URL-safe character set (`A-Z a-z 0-9 - _`)
- No hardcoded fallback — if `POSTGRES_PASSWORD` is unset, connection fails with empty password

### Port Exposure

Docker Compose maps the database port to the host:

```yaml
services:
  db:
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
```

| Environment  | Recommendation                                         |
| :----------- | :----------------------------------------------------- |
| Local dev    | Default `5432` mapping is fine                         |
| Production   | Remove `ports` mapping; access only via Docker network |
| Cloud server | Firewall rules to block external access to 5432        |

---

## Docker Network Isolation

### Internal Communication

In OneBase's Docker Compose architecture, services communicate via an internal network:

```
┌─────────────────────────────────────────┐
│          Docker Internal Network        │
│                                         │
│  backend ──(db:5432)──▶ db (PostgreSQL) │
│  backend ──(ollama:11434)──▶ ollama     │
│                                         │
└─────────────────────────────────────────┘
        │                          
   ports: 8000                     
        ▼                          
    Host / External Access          
```

- **Backend → Database**: Via service name `db`, doesn't go through host network
- **Backend → Ollama**: Via service name `ollama` or `host.docker.internal`
- **Only exposed**: Backend API port (default 8000)

### host.docker.internal Rewrite

When containers need to access host services, OneBase automatically rewrites `localhost` to `host.docker.internal`:

```python
# onebase/factory.py
def _docker_rewrite(url: str) -> str:
    if os.getenv("RUNNING_IN_DOCKER") == "true":
        return url.replace("localhost", "host.docker.internal")
    return url
```

This ensures containers can correctly access services like Ollama running on the host. The `extra_hosts` config in `docker-compose.yml` ensures DNS resolution:

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

---

## Production Deployment Checklist

Before deploying to the public internet, check each item:

- [ ] `.env` is excluded from version control
- [ ] `POSTGRES_PASSWORD` uses a strong random password
- [ ] `API_TOKEN` is set to a strong random string
- [ ] `CORS_ORIGINS` is set to your actual frontend domain (not `*`)
- [ ] Database port is not exposed to the internet (remove `ports` or configure firewall)
- [ ] API keys use minimum-privilege policies
- [ ] Backend port is served over HTTPS via reverse proxy (Nginx / Caddy)
- [ ] Docker images use fixed version tags, not `latest`

---

## Related Documentation

- [Database Configuration](database.md) — Credential field details
- [Engine Configuration](engine.md) — API key to provider mapping
- [Configuration Reference](overview.en.md#environment-variables-reference-env) — Environment variable reference