# Engine Configuration

`engine` is the most critical field in `onebase.yml`. It determines which LLM OneBase uses for **reasoning** (Q&A) and **text embedding** (vectorization).

---

## Basic Structure

```yaml title="onebase.yml"
engine:
  reasoning:
    provider: <provider identifier>
    model: <model name>
  embedding:
    provider: <provider identifier>
    model: <model name>
```

`engine` contains two required sub-fields:

| Sub-field   | Purpose   | Description                                             |
| :---------- | :-------- | :------------------------------------------------------ |
| `reasoning` | Reasoning | The LLM that processes questions and generates answers  |
| `embedding` | Embedding | Converts document text into vectors for semantic search |

Each sub-field requires a `provider` (provider identifier) and `model` (model name).

---

## Provider Identifiers

`provider` determines which SDK/API OneBase uses to communicate with the model. All supported identifiers:

| provider        | Service               | Reasoning | Embedding | Required Env Vars                                               |
| :-------------- | :-------------------- | :-------: | :-------: | :-------------------------------------------------------------- |
| `openai`        | OpenAI / Compatible   |     ✅     |     ✅     | `OPENAI_API_KEY`, optional `OPENAI_BASE_URL`                    |
| `ollama`        | Ollama (Local)        |     ✅     |     ✅     | No key needed, optional `OLLAMA_BASE_URL`                       |
| `dashscope`     | Alibaba Cloud Bailian |     ✅     |     ✅     | `DASHSCOPE_API_KEY`                                             |
| `zhipu`         | Zhipu AI / GLM        |     ✅     |     ✅     | `ZHIPU_API_KEY`                                                 |
| `anthropic`     | Anthropic / Claude    |     ✅     |     ❌     | `ANTHROPIC_API_KEY`                                             |
| `google`        | Google Gemini         |     ✅     |     ✅     | `GOOGLE_API_KEY`                                                |
| `google-vertex` | Google Vertex AI      |     ✅     |     ✅     | `GOOGLE_APPLICATION_CREDENTIALS`, `GOOGLE_CLOUD_PROJECT`        |
| `deepseek`      | DeepSeek              |     ✅     |     ❌     | `DEEPSEEK_API_KEY`                                              |
| `qianfan`       | Baidu Qianfan         |     ✅     |     ✅     | `QIANFAN_AK`, `QIANFAN_SK`                                      |
| `groq`          | Groq                  |     ✅     |     ❌     | `GROQ_API_KEY`                                                  |
| `modelscope`    | ModelScope            |     ✅     |     ✅     | `MODELSCOPE_SDK_TOKEN`                                          |
| `doubao`        | ByteDance Doubao      |     ✅     |     ✅     | `VOLC_ACCESS_KEY`, `VOLC_SECRET_KEY`, `VOLC_ENGINE_ENDPOINT_ID` |
| `siliconflow`   | SiliconFlow           |     ✅     |     ✅     | `SILICONFLOW_API_KEY`                                           |

!!! warning "Embedding Limitations"
    `anthropic`, `deepseek`, and `groq` do not provide Embedding APIs. If you use these for Reasoning, pair Embedding with another provider such as `ollama` or `dashscope`.

---

## Model Names

The `model` field takes the model ID from the corresponding provider. Naming conventions vary — consult each provider's API docs. Common examples:

| provider      | Reasoning Model Examples             | Embedding Model Examples                           |
| :------------ | :----------------------------------- | :------------------------------------------------- |
| `openai`      | `gpt-4o-mini`, `gpt-4o`              | `text-embedding-3-small`, `text-embedding-3-large` |
| `ollama`      | `deepseek-r1:1.5b`, `llama3.2`       | `nomic-embed-text:v1.5`, `bge-m3`                  |
| `dashscope`   | `qwen-turbo`, `deepseek-v3`          | `text-embedding-v4`                                |
| `zhipu`       | `glm-4-flash`, `glm-4`               | `embedding-3`                                      |
| `anthropic`   | `claude-sonnet-4-20250514`           | —                                                  |
| `google`      | `gemini-2.0-flash`                   | `text-embedding-004`                               |
| `deepseek`    | `deepseek-chat`, `deepseek-reasoner` | —                                                  |
| `qianfan`     | `ERNIE-4.0-8K`                       | `bge-large-zh`                                     |
| `groq`        | `llama-3.3-70b-versatile`            | —                                                  |
| `doubao`      | `doubao-1.5-pro-32k`                 | `doubao-embedding`                                 |
| `siliconflow` | `deepseek-ai/DeepSeek-V3`            | `BAAI/bge-m3`                                      |

---

## Configuration Examples

### Cloud: OpenAI Full Stack

```yaml
engine:
  reasoning:
    provider: openai
    model: gpt-4o-mini
  embedding:
    provider: openai
    model: text-embedding-3-small
```

```bash title=".env"
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxx
```

### Cloud: Hybrid (DeepSeek Reasoning + Alibaba Embedding)

Reasoning and embedding can use **different providers** — OneBase bridges them automatically:

```yaml
engine:
  reasoning:
    provider: deepseek
    model: deepseek-chat
  embedding:
    provider: dashscope
    model: text-embedding-v4
```

```bash title=".env"
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxx
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxx
```

### Local: Ollama Fully Offline

No API key needed. Ensure [Ollama](https://ollama.com) is installed on the host and models are downloaded:

```yaml
engine:
  reasoning:
    provider: ollama
    model: deepseek-r1:1.5b
  embedding:
    provider: ollama
    model: nomic-embed-text:v1.5
```

You can also use `--with-ollama` to let OneBase manage the Ollama container:

```bash
onebase build --with-ollama -g
onebase serve --with-ollama -g -d
```

### Local: Xinference / vLLM (OpenAI-Compatible)

Connect local inference frameworks via OpenAI-compatible API. Set `provider` to `openai` and specify the local API URL in `.env`:

```yaml
engine:
  reasoning:
    provider: openai
    model: qwen2.5-7b-instruct     # Model deployed in your local framework
  embedding:
    provider: ollama                # Embedding can use a different engine
    model: nomic-embed-text:v1.5
```

```bash title=".env"
OPENAI_BASE_URL=http://localhost:9997/v1
OPENAI_API_KEY=dummy-key
```

!!! tip "Automatic localhost rewrite"
    Just write `localhost` in `.env`. When running inside a container, OneBase automatically rewrites it to `host.docker.internal` — no manual Docker networking needed.

---

## Network Addressing

Since the OneBase backend runs inside a Docker container, accessing local model services on the host requires special handling. OneBase has built-in automatic network rewriting:

| Value in `.env`             | Actually used in container            | Description            |
| :-------------------------- | :------------------------------------ | :--------------------- |
| `http://localhost:9997/v1`  | `http://host.docker.internal:9997/v1` | Auto-rewritten         |
| `http://127.0.0.1:11434`    | `http://host.docker.internal:11434`   | Auto-rewritten         |
| `https://api.openai.com/v1` | `https://api.openai.com/v1`           | Cloud URL, unchanged   |
| Not set (Ollama default)    | `http://host.docker.internal:11434`   | Default also rewritten |

When using `--with-ollama` / `--with-xinference` / `--with-vllm`, OneBase automatically sets internal Docker network addresses (e.g., `http://ollama:11434`), so no manual URL configuration is needed.

---

## Environment Variable Reference

All API keys and connection URLs are configured via the `.env` file in the project root. Only fill in providers you actually use:

```bash title=".env"
# ---- OpenAI / Compatible ----
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxx
OPENAI_BASE_URL=                          # Optional, for local inference

# ---- Ollama ----
OLLAMA_BASE_URL=                          # Optional, default http://localhost:11434

# ---- Alibaba Cloud Bailian ----
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxx

# ---- DeepSeek ----
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxx

# ---- Anthropic / Claude ----
ANTHROPIC_API_KEY=sk-xxxxxxxxxxxx

# ---- Google Gemini ----
GOOGLE_API_KEY=xxxxxxxxxxxx

# ---- Google Vertex AI ----
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GOOGLE_CLOUD_PROJECT=my-gcp-project
VERTEX_LOCATION=us-central1              # Optional, default us-central1

# ---- Zhipu AI ----
ZHIPU_API_KEY=xxxxxxxxxxxx.xxxxxxxxxxxx

# ---- Baidu Qianfan ----
QIANFAN_AK=xxxxxxxxxxxx
QIANFAN_SK=xxxxxxxxxxxx

# ---- Groq ----
GROQ_API_KEY=gsk_xxxxxxxxxxxx

# ---- ModelScope ----
MODELSCOPE_SDK_TOKEN=xxxxxxxxxxxx

# ---- ByteDance Doubao ----
VOLC_ACCESS_KEY=xxxxxxxxxxxx
VOLC_SECRET_KEY=xxxxxxxxxxxx
VOLC_ENGINE_ENDPOINT_ID=xxxxxxxxxxxx

# ---- SiliconFlow ----
SILICONFLOW_API_KEY=sk-xxxxxxxxxxxx
```

---

## FAQ

### Do reasoning and embedding have to use the same provider?

No. `reasoning` and `embedding` are completely independent and can be freely combined. For example, using DeepSeek for reasoning and Ollama for local embedding is a perfectly valid configuration.

### Must the embedding model be the same for build and serve?

Yes, otherwise it will error. Different embedding models produce vectors with different dimensions and semantic spaces, making old vector data incompatible.

### Do I need to rebuild after changing models?

- **Only changed the `reasoning` model**: No rebuild needed — just run `onebase serve -d` to apply.
- **Changed the `embedding` model**: You must re-run `onebase build`, as different embedding models produce incompatible vectors.

### What's the difference between OPENAI_BASE_URL and OPENAI_API_BASE?

Both are supported. `OPENAI_BASE_URL` is the official OpenAI SDK naming; `OPENAI_API_BASE` is the legacy name. If both are set, `OPENAI_BASE_URL` takes priority.

### Does Google Vertex AI need special handling?

Yes. Vertex AI uses service account JSON key file authentication. You need to mount the key file into the container and specify the path in `.env`. This may require manually editing the generated `docker-compose.yml`.
