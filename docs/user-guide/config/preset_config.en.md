# Preset Configurations

OneBase provides preset configuration templates for common use cases. You can copy them directly or modify as needed.

---

## Zero-Cost Local Experience

Fully offline, using Ollama to run local small models. No API key required.

```yaml title="onebase.yml"
site_name: Local Knowledge Base
engine:
  reasoning:
    provider: ollama
    model: deepseek-r1:1.5b
  embedding:
    provider: ollama
    model: nomic-embed-text:v1.5
database:
  type: postgresql
  vector_store: pgvector
knowledge_base:
  path: ./base
  chunk_size: 500
  struct: default
features:
  chat_history: true
  file_upload: true
```

```bash title=".env"
POSTGRES_USER=onebase
POSTGRES_PASSWORD=your_random_password
POSTGRES_DB=onebase_db
```

**Launch:**

```bash
onebase build --with-ollama -g   # Auto-start Ollama container + GPU
onebase serve --with-ollama -g -d
```

---

## China Cloud (Alibaba Cloud Bailian / DashScope)

Using Qwen series models with direct China network access, no proxy needed.

```yaml title="onebase.yml"
site_name: Enterprise Knowledge Assistant
engine:
  reasoning:
    provider: dashscope
    model: qwen-turbo
  embedding:
    provider: dashscope
    model: text-embedding-v4
database:
  type: postgresql
  vector_store: pgvector
knowledge_base:
  path: ./base
  chunk_size: 500
  struct: default
features:
  chat_history: true
  file_upload: true
```

```bash title=".env"
POSTGRES_USER=onebase
POSTGRES_PASSWORD=your_random_password
POSTGRES_DB=onebase_db
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxx
```

---

## Global Cloud (OpenAI)

Using OpenAI GPT series, suitable for users with international network access.

```yaml title="onebase.yml"
site_name: AI Knowledge Base
engine:
  reasoning:
    provider: openai
    model: gpt-4o-mini
  embedding:
    provider: openai
    model: text-embedding-3-small
database:
  type: postgresql
  vector_store: pgvector
knowledge_base:
  path: ./base
  chunk_size: 500
  struct: default
features:
  chat_history: true
  file_upload: true
```

```bash title=".env"
POSTGRES_USER=onebase
POSTGRES_PASSWORD=your_random_password
POSTGRES_DB=onebase_db
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxx
```

---

## Hybrid Setup (DeepSeek Reasoning + Local Embedding)

DeepSeek for reasoning + Ollama local embedding — balancing quality and cost.

```yaml title="onebase.yml"
site_name: Hybrid Knowledge Base
engine:
  reasoning:
    provider: deepseek
    model: deepseek-chat
  embedding:
    provider: ollama
    model: bge-m3
database:
  type: postgresql
  vector_store: pgvector
knowledge_base:
  path: ./base
  chunk_size: 800
  struct: default
features:
  chat_history: true
  file_upload: false
```

```bash title=".env"
POSTGRES_USER=onebase
POSTGRES_PASSWORD=your_random_password
POSTGRES_DB=onebase_db
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxx
```

---

## Read-Only Knowledge Base (No Upload, No Chat History)

Suitable for product documentation sites with pure retrieval Q&A.

```yaml title="onebase.yml"
site_name: Product FAQ
engine:
  reasoning:
    provider: dashscope
    model: qwen-turbo
  embedding:
    provider: dashscope
    model: text-embedding-v4
database:
  type: postgresql
  vector_store: pgvector
knowledge_base:
  path: ./base
  chunk_size: 300
  struct: default
features:
  chat_history: false
  file_upload: false
```
