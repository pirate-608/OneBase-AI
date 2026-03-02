# 预设配置

OneBase 提供了一些针对常见使用场景的预设配置模板，你可以直接复制使用或在此基础上修改。

---

## 零成本本地体验

完全离线，使用 Ollama 运行本地小模型，无需任何 API Key。

```yaml title="onebase.yml"
site_name: 本地知识库
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

**启动方式：**

```bash
onebase build --with-ollama -g   # 自动拉起 Ollama 容器 + GPU
onebase serve --with-ollama -g -d
```

---

## 国内云端（阿里云百炼）

使用通义千问系列模型，国内网络直连，无需代理。

```yaml title="onebase.yml"
site_name: 企业知识助手
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

## 海外云端（OpenAI）

使用 OpenAI GPT 系列，适合有海外网络条件的用户。

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

## 混合搭配（DeepSeek 推理 + 本地向量化）

用 DeepSeek 的推理能力 + Ollama 本地 Embedding，兼顾效果与成本。

```yaml title="onebase.yml"
site_name: 混合知识库
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

## 只读知识库（禁用上传和对话历史）

适合嵌入到产品文档站的纯检索问答场景。

```yaml title="onebase.yml"
site_name: 产品 FAQ
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
