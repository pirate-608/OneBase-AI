OneBase adopts a convention-over-configuration approach for knowledge base customization. It reads a single core file `onebase.yml` to import all user-defined configuration, uses `.env` files to add sensitive information as environment variables, and injects these settings into the service runtime. When filling in `onebase.yml`, you must follow the specified format.

Here is a complete configuration example:

```yaml title="onebase.yml"
# ---- Site Name (required) ----
site_name: My AI Assistant

# ---- Engine Configuration (required) ----
engine:
  reasoning:                    # Reasoning engine
    provider: ollama            # Provider identifier
    model: deepseek-r1:1.5b     # Model name
  embedding:                    # Embedding engine
    provider: ollama
    model: nomic-embed-text:v1.5

# ---- Database Configuration ----
database:
  type: postgresql              # Only postgresql supported
  vector_store: pgvector        # Only pgvector supported

# ---- Knowledge Base Configuration ----
knowledge_base:
  path: ./base                  # Document root directory
  chunk_size: 500               # Chunk size (characters), must be > 0
  struct: default               # Directory structure: default or manual

# ---- Feature Flags ----
features:
  chat_history: true            # Multi-turn chat history
  file_upload: true             # Frontend file upload

# ---- Performance & Stability ----
performance:
  redis_cache_enabled: true            # Enable Redis context cache
  redis_context_cache_ttl_seconds: 300 # Context cache TTL in seconds
  rate_limit_enabled: true             # Enable API rate limiting
  chat_rate_limit_per_minute: 30       # /api/chat requests per minute
  upload_rate_limit_per_minute: 6      # /api/upload requests per minute
```

## Configuration Field Reference

| Field                                         | Type           | Required | Default      | Description                                                |
| :-------------------------------------------- | :------------- | :------: | :----------- | :--------------------------------------------------------- |
| `site_name`                                   | string         |    ✅     | —            | Site name, displayed in the frontend title bar             |
| `engine.reasoning.provider`                   | string         |    ✅     | —            | Reasoning provider, see [Engine Config](engine.md)         |
| `engine.reasoning.model`                      | string         |    ✅     | —            | Reasoning model name                                       |
| `engine.embedding.provider`                   | string         |    ✅     | —            | Embedding provider                                         |
| `engine.embedding.model`                      | string         |    ✅     | —            | Embedding model name                                       |
| `database.type`                               | Literal        |    —     | `postgresql` | Database type, only `postgresql` supported                 |
| `database.vector_store`                       | Literal        |    —     | `pgvector`   | Vector store, only `pgvector` supported                    |
| `knowledge_base.path`                         | string         |    —     | `./base`     | Knowledge base document root path                          |
| `knowledge_base.chunk_size`                   | int            |    —     | `500`        | Text chunk size, must be > 0                               |
| `knowledge_base.struct`                       | string \| dict |    —     | `default`    | Directory mapping, see [Knowledge Base](knowledge_base.md) |
| `features.chat_history`                       | bool           |    —     | `true`       | Enable chat history                                        |
| `features.file_upload`                        | bool           |    —     | `true`       | Enable frontend file upload                                |
| `performance.redis_cache_enabled`             | bool           |    —     | `true`       | Enable Redis retrieval context cache                       |
| `performance.redis_context_cache_ttl_seconds` | int            |    —     | `300`        | Redis context cache TTL in seconds                         |
| `performance.rate_limit_enabled`              | bool           |    —     | `true`       | Enable backend API rate limiting                           |
| `performance.chat_rate_limit_per_minute`      | int            |    —     | `30`         | Max requests per minute for `/api/chat`                    |
| `performance.upload_rate_limit_per_minute`    | int            |    —     | `6`          | Max requests per minute for `/api/upload`                  |

---

## Environment Variables Reference (.env)

| Variable                    | Purpose               | Required | Description                                          |
| :-------------------------- | :-------------------- | :------: | :--------------------------------------------------- |
| `POSTGRES_USER`             | Database username     |    —     | Default `onebase`                                    |
| `POSTGRES_PASSWORD`         | Database password     |    ✅     | Auto-generated by `onebase init`                     |
| `POSTGRES_DB`               | Database name         |    —     | Default `onebase_db`                                 |
| `POSTGRES_HOST`             | Database host         |    —     | Default `localhost`                                  |
| `POSTGRES_PORT`             | Database port         |    —     | Default `5432`                                       |
| `OPENAI_API_KEY`            | OpenAI API key        |    ⚡     | Required when provider is `openai`                   |
| `OPENAI_BASE_URL`           | OpenAI-compatible URL |    —     | For local inference frameworks                       |
| `OLLAMA_BASE_URL`           | Ollama service URL    |    —     | Default `http://localhost:11434`                     |
| `DASHSCOPE_API_KEY`         | Alibaba Bailian key   |    ⚡     | Required for `dashscope` provider                    |
| `DEEPSEEK_API_KEY`          | DeepSeek key          |    ⚡     | Required for `deepseek` provider                     |
| `ANTHROPIC_API_KEY`         | Anthropic key         |    ⚡     | Required for `anthropic` provider                    |
| `GOOGLE_API_KEY`            | Google Gemini key     |    ⚡     | Required for `google` provider                       |
| `ZHIPU_API_KEY`             | Zhipu AI key          |    ⚡     | Required for `zhipu` provider                        |
| `GROQ_API_KEY`              | Groq key              |    ⚡     | Required for `groq` provider                         |
| `QIANFAN_AK` / `QIANFAN_SK` | Baidu Qianfan keys    |    ⚡     | Required for `qianfan` provider                      |
| `SILICONFLOW_API_KEY`       | SiliconFlow key       |    ⚡     | Required for `siliconflow` provider                  |
| `REDIS_URL`                 | Redis connection URL  |    —     | Used for context cache and distributed rate limiting |

⚡ = Required when using the corresponding provider

---

## Related Documentation

- [Engine Configuration](engine.md) — Provider and model details
- [Database Configuration](database.md) — Connection credentials
- [Knowledge Base](knowledge_base.md) — Directory mapping rules
- [Feature Flags](features.md) — chat_history and file_upload behavior
- [Model Support](MODELS.md) — All supported model providers
- [Preset Configurations](preset_config.md) — Common scenario templates
