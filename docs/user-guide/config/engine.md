# Engine 引擎配置

`engine` 是 `onebase.yml` 中最核心的配置字段，它决定了 OneBase 使用哪个大模型进行**推理问答**（Reasoning）和**文本向量化**（Embedding）。

---

## 基本结构

```yaml title="onebase.yml"
engine:
  reasoning:
    provider: <服务商标识符>
    model: <模型名称>
  embedding:
    provider: <服务商标识符>
    model: <模型名称>
```

`engine` 包含两个必填子字段：

| 子字段      | 用途     | 说明                               |
| :---------- | :------- | :--------------------------------- |
| `reasoning` | 推理引擎 | 处理用户提问、生成回答的大语言模型 |
| `embedding` | 向量引擎 | 将文档文本转化为向量，用于语义检索 |

每个子字段都需要指定 `provider`（服务商标识符）和 `model`（模型名称）。

---

## provider 标识符

`provider` 决定了 OneBase 通过哪个 SDK/API 与模型通信。以下是所有支持的标识符：

| provider        | 服务商             | 支持 Reasoning | 支持 Embedding | 所需环境变量                                                    |
| :-------------- | :----------------- | :------------: | :------------: | :-------------------------------------------------------------- |
| `openai`        | OpenAI / 兼容接口  |       ✅        |       ✅        | `OPENAI_API_KEY`，可选 `OPENAI_BASE_URL`                        |
| `ollama`        | Ollama（本地）     |       ✅        |       ✅        | 无需 Key，可选 `OLLAMA_BASE_URL`                                |
| `dashscope`     | 阿里云百炼 / 通义  |       ✅        |       ✅        | `DASHSCOPE_API_KEY`                                             |
| `zhipu`         | 智谱 AI / GLM      |       ✅        |       ✅        | `ZHIPU_API_KEY`                                                 |
| `anthropic`     | Anthropic / Claude |       ✅        |       ❌        | `ANTHROPIC_API_KEY`                                             |
| `google`        | Google Gemini      |       ✅        |       ✅        | `GOOGLE_API_KEY`                                                |
| `google-vertex` | Google Vertex AI   |       ✅        |       ✅        | `GOOGLE_APPLICATION_CREDENTIALS`、`GOOGLE_CLOUD_PROJECT`        |
| `deepseek`      | DeepSeek           |       ✅        |       ❌        | `DEEPSEEK_API_KEY`                                              |
| `qianfan`       | 百度千帆           |       ✅        |       ✅        | `QIANFAN_AK`、`QIANFAN_SK`                                      |
| `groq`          | Groq               |       ✅        |       ❌        | `GROQ_API_KEY`                                                  |
| `modelscope`    | 魔搭社区           |       ✅        |       ✅        | `MODELSCOPE_SDK_TOKEN`                                          |
| `doubao`        | 字节跳动豆包       |       ✅        |       ✅        | `VOLC_ACCESS_KEY`、`VOLC_SECRET_KEY`、`VOLC_ENGINE_ENDPOINT_ID` |
| `siliconflow`   | 硅基流动           |       ✅        |       ✅        | `SILICONFLOW_API_KEY`                                           |
| `docker-model`  | Docker 原生模型    |       ✅        |       ✅        | 无需 Key（Docker Desktop 4.40+）                                |

!!! warning "Embedding 限制"
    `anthropic`、`deepseek`、`groq` 不提供 Embedding 接口。如果 Reasoning 使用了这些服务商，Embedding 需要搭配其他 provider，例如 `ollama`、`dashscope` 或 `docker-model`。

---

## model 模型名称

`model` 字段填写对应服务商的模型 ID。不同服务商的命名规则不同，请参阅各自的 API 文档。常见示例：

| provider       | 推理模型示例                         | 向量模型示例                                       |
| :------------- | :----------------------------------- | :------------------------------------------------- |
| `openai`       | `gpt-4o-mini`、`gpt-4o`              | `text-embedding-3-small`、`text-embedding-3-large` |
| `ollama`       | `deepseek-r1:1.5b`、`llama3.2`       | `nomic-embed-text:v1.5`、`bge-m3`                  |
| `dashscope`    | `qwen-turbo`、`deepseek-v3`          | `text-embedding-v4`                                |
| `zhipu`        | `glm-4-flash`、`glm-4`               | `embedding-3`                                      |
| `anthropic`    | `claude-sonnet-4-20250514`           | —                                                  |
| `google`       | `gemini-2.0-flash`                   | `text-embedding-004`                               |
| `deepseek`     | `deepseek-chat`、`deepseek-reasoner` | —                                                  |
| `qianfan`      | `ERNIE-4.0-8K`                       | `bge-large-zh`                                     |
| `groq`         | `llama-3.3-70b-versatile`            | —                                                  |
| `doubao`       | `doubao-1.5-pro-32k`                 | `doubao-embedding`                                 |
| `siliconflow`  | `deepseek-ai/DeepSeek-V3`            | `BAAI/bge-m3`                                      |
| `docker-model` | `ai/qwen2.5:7B-Q4_K_M`               | `ai/bge-m3:Q4_K_M`                                 |

---

## 配置示例

### 云端：OpenAI 全家桶

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

### 云端：混合搭配（DeepSeek 推理 + 阿里云向量化）

推理和向量化可以使用**不同的服务商**，OneBase 会自动桥接：

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

### 本地：Ollama 全离线

无需任何 API Key，确保宿主机已安装 [Ollama](https://ollama.com) 并下载模型即可：

```yaml
engine:
  reasoning:
    provider: ollama
    model: deepseek-r1:1.5b
  embedding:
    provider: ollama
    model: nomic-embed-text:v1.5
```

也可以用 `--with-ollama` 让 OneBase 自动管理 Ollama 容器（模型会在首次启动时自动拉取，无需手动下载）：

```bash
onebase build --with-ollama -g
onebase serve --with-ollama -g -d
```

### 本地：Docker Model Runner（最简方案，Docker Desktop 4.40+）

如果你使用的是 Docker Desktop 4.40 及以上版本，可以直接使用 Docker 原生的模型管理器来运行本地大模型，无需安装任何第三方推理框架：

```yaml
engine:
  reasoning:
    provider: docker-model
    model: ai/qwen2.5:7B-Q4_K_M
  embedding:
    provider: docker-model
    model: ai/bge-m3:Q4_K_M
```

```bash
onebase build --with-docker-model
onebase serve --with-docker-model -d
```

Docker 会自动通过 `docker model` 拉取和管理模型，后端通过 `http://model-runner.docker.internal/engines/llama.cpp/v1` 直接访问 OpenAI 兼容 API，无需任何 API Key 或额外网络配置。

!!! tip "Docker Model Runner 的优势"
    - 零配置：无需安装 Ollama / vLLM 等第三方工具
    - 原生管理：模型由 Docker Desktop 统一管理，与容器生命周期解耦
    - 内置引擎：使用 llama.cpp 后端，支持 GGUF 量化模型
    - 无缝网络：容器内直接通过 Docker 内部 DNS 访问，无需端口映射

### 本地：Xinference / vLLM（OpenAI 兼容方案）

将本地推理框架通过 OpenAI 兼容接口接入。`provider` 设为 `openai`，并在 `.env` 中指定本地 API 地址：

```yaml
engine:
  reasoning:
    provider: openai
    model: qwen2.5-7b-instruct     # 你在本地框架中部署的模型名
  embedding:
    provider: ollama                # 向量化可以用其他引擎
    model: nomic-embed-text:v1.5
```

```bash title=".env"
OPENAI_BASE_URL=http://localhost:9997/v1
OPENAI_API_KEY=dummy-key
```

!!! tip "localhost 自动重写"
    在 `.env` 中直接写 `localhost` 即可。OneBase 在容器内运行时会自动将其重写为 `host.docker.internal`，无需手动处理 Docker 网络地址。

---

## 网络寻址机制

由于 OneBase 后端运行在 Docker 容器内，访问宿主机上的本地模型服务需要特殊处理。OneBase 内置了自动网络重写：

| 用户 `.env` 中填写          | 容器内实际使用                        | 说明             |
| :-------------------------- | :------------------------------------ | :--------------- |
| `http://localhost:9997/v1`  | `http://host.docker.internal:9997/v1` | 自动重写         |
| `http://127.0.0.1:11434`    | `http://host.docker.internal:11434`   | 自动重写         |
| `https://api.openai.com/v1` | `https://api.openai.com/v1`           | 云端地址，不处理 |
| 不填（Ollama 默认）         | `http://host.docker.internal:11434`   | 默认值也会被重写 |

使用 `--with-ollama` / `--with-xinference` / `--with-vllm` / `--with-docker-model` 参数时，OneBase 会自动设置容器间内网地址（如 `http://ollama:11434`），此时无需手动配置任何 URL。

---

## 环境变量参考

所有 API 密钥和连接地址均通过项目根目录的 `.env` 文件配置。只需填写你实际使用的服务商：

```bash title=".env"
# ---- OpenAI / 兼容接口 ----
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxx
OPENAI_BASE_URL=                          # 可选，本地推理框架时填写

# ---- Ollama ----
OLLAMA_BASE_URL=                          # 可选，默认 http://localhost:11434

# ---- 阿里云百炼 ----
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
VERTEX_LOCATION=us-central1              # 可选，默认 us-central1

# ---- 智谱 AI ----
ZHIPU_API_KEY=xxxxxxxxxxxx.xxxxxxxxxxxx

# ---- 百度千帆 ----
QIANFAN_AK=xxxxxxxxxxxx
QIANFAN_SK=xxxxxxxxxxxx

# ---- Groq ----
GROQ_API_KEY=gsk_xxxxxxxxxxxx

# ---- 魔搭社区 ----
MODELSCOPE_SDK_TOKEN=xxxxxxxxxxxx

# ---- 字节跳动豆包 ----
VOLC_ACCESS_KEY=xxxxxxxxxxxx
VOLC_SECRET_KEY=xxxxxxxxxxxx
VOLC_ENGINE_ENDPOINT_ID=xxxxxxxxxxxx

# ---- 硅基流动 ----
SILICONFLOW_API_KEY=sk-xxxxxxxxxxxx
```

---

## 常见问题

### 推理和向量化必须用同一个 provider 吗？

不需要。`reasoning` 和 `embedding` 是完全独立的，可以自由搭配。例如用 DeepSeek 做推理，用 Ollama 做本地向量化，这是完全合法的配置。

### build和serve时的向量化模型必须是同一个吗？

需要，否则会报错。

### 我换了模型，需要重新 build 吗？

- **只换了 `reasoning` 模型**：不需要重新 build，直接 `onebase serve -d` 即可生效。
- **换了 `embedding` 模型**：需要重新执行 `onebase build`，因为不同 Embedding 模型产生的向量维度和语义空间不同，旧的向量数据不兼容。

### build和serve时的向量化模型必须是同一个吗？

必须，否则会报错。原因同上

### OPENAI_BASE_URL 和 OPENAI_API_BASE 有什么区别？

两者都支持，`OPENAI_BASE_URL` 是 OpenAI SDK 的官方命名，`OPENAI_API_BASE` 是旧版命名。如果同时设置，`OPENAI_BASE_URL` 优先。

### Google Vertex AI 需要特殊处理吗？

是的。Vertex AI 使用服务账号 JSON 密钥文件认证，你需要将密钥文件挂载到容器内，并在 `.env` 中指定路径。这可能需要手动修改生成的 `docker-compose.yml`。
