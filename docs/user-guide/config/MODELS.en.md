<h1 align="center">
  <img src="https://onebase.67656.fun/assets/images/onebase.svg" width="40" height="40" style="vertical-align: middle; margin-right: 10px;" alt="OneBase Logo">
  OneBase AI Model Support & Configuration
</h1>

OneBase follows the design philosophy of "complete decoupling between application layer and inference layer". Through a unified Model Factory, it natively supports most mainstream cloud APIs and local LLM inference frameworks worldwide.

## 🌟 Supported Cloud Model Providers

In the `onebase.yml` configuration file, you can freely combine different reasoning and embedding engines:

| Provider                                                                 | Identifier (provider) | Reasoning | Embedding | Environment Variables                                                                                                                                       | Base URL                                                                                                 | OpenAI Compatible | API Docs                                                                               |
| :----------------------------------------------------------------------- | :-------------------- | :-------- | :-------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------- | :---------------- | :------------------------------------------------------------------------------------- |
| [OpenAI](https://openai.com)                                             | `openai`              | ✅         | ✅         | `OPENAI_API_KEY`                                                                                                                                            | `https://api.openai.com/v1`                                                                              | ✅                 | [View](https://platform.openai.com/docs/api-reference)                                 |
| [Ollama](https://ollama.com) (Local)                                     | `ollama`              | ✅         | ✅         | (Ready to use, no key needed)                                                                                                                               | `http://localhost:11434`                                                                                 | ✅                 | [View](https://docs.ollama.com/api/introduction)                                       |
| [Anthropic / Claude](https://www.anthropic.com)                          | `anthropic`           | ✅         | ❌         | `ANTHROPIC_API_KEY`                                                                                                                                         | `https://api.anthropic.com/v1`                                                                           | ❌                 | [View](https://docs.anthropic.com/en/api/getting-started)                              |
| [Google Gemini](https://deepmind.google/technologies/gemini/)            | `google`              | ✅         | ✅         | `GOOGLE_API_KEY`                                                                                                                                            | `https://generativelanguage.googleapis.com/v1beta`                                                       | ✅                 | [View](https://ai.google.dev/gemini-api/docs)                                          |
| [Google Vertex AI](https://cloud.google.com/vertex-ai)                   | `google-vertex`       | ✅         | ✅         | `GOOGLE_APPLICATION_CREDENTIALS` (Service account JSON key path); `GOOGLE_CLOUD_PROJECT` (Project ID); `VERTEX_LOCATION`: Optional, defaults to us-central1 | `https://LOCATION-aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/LOCATION/publishers/google` | ⚠️                 | [View](https://cloud.google.com/vertex-ai/docs/reference)                              |
| [Groq](https://groq.com)                                                 | `groq`                | ✅         | ❌         | `GROQ_API_KEY`                                                                                                                                              | `https://api.groq.com/openai/v1`                                                                         | ✅                 | [View](https://console.groq.com/docs/api-reference)                                    |
| [Alibaba Cloud Bailian / Tongyi](https://www.aliyun.com/product/bailian) | `dashscope`           | ✅         | ✅         | `DASHSCOPE_API_KEY`                                                                                                                                         | `https://dashscope.aliyuncs.com/compatible-mode/v1`                                                      | ✅                 | [View](https://help.aliyun.com/model-studio/get-api-key)                               |
| [Zhipu AI / GLM](https://www.zhipuai.cn)                                 | `zhipu`               | ✅         | ✅         | `ZHIPU_API_KEY`                                                                                                                                             | `https://open.bigmodel.cn/api/paas/v4`                                                                   | ✅                 | [View](https://docs.bigmodel.cn/cn/api)                                                |
| [ModelScope](https://www.modelscope.cn)                                  | `modelscope`          | ✅         | ✅         | `MODELSCOPE_SDK_TOKEN` (Online invocation)                                                                                                                  | `https://api.modelscope.cn/v1`                                                                           | ❌                 | [View](https://www.modelscope.cn/docs)                                                 |
| [Baidu Qianfan](https://cloud.baidu.com/product/wenxinworkshop)          | `qianfan`             | ✅         | ✅         | `QIANFAN_AK` & `QIANFAN_SK`                                                                                                                                 | `https://qianfan.baidubce.com/v2`                                                                        | ✅                 | [View](https://cloud.baidu.com/doc/WENXINWORKSHOP/index.html)                          |
| [DeepSeek](https://www.deepseek.com)                                     | `deepseek`            | ✅         | ❌         | `DEEPSEEK_API_KEY`                                                                                                                                          | `https://api.deepseek.com/v1`                                                                            | ✅                 | [View](https://platform.deepseek.com/api-docs/)                                        |
| [ByteDance Doubao](https://www.volcengine.com/product/doubao)            | `doubao`              | ✅         | ✅         | `VOLC_ACCESS_KEY` (Volcengine Access Key) `VOLC_SECRET_KEY` (Volcengine Secret Key) `VOLC_ENGINE_ENDPOINT_ID` (Volcengine Ark Endpoint ID)                  | `https://ark.cn-beijing.volces.com/api/v3`                                                               | ✅                 | [View](https://www.volcengine.com/docs/82379/1541594)                                  |
| [SiliconFlow](https://siliconflow.cn)                                    | `siliconflow`         | ✅         | ✅         | `SILICONFLOW_API_KEY`                                                                                                                                       | `https://api.siliconflow.cn/v1`                                                                          | ✅                 | [View](https://docs.siliconflow.cn/cn/api-reference/chat-completions/chat-completions) |

⚠️ **Note:** Google Vertex requires mounting the service account JSON key file into the container, which may require manual code adjustments!

💡 **Tip:** You can set the reasoning engine to `deepseek` and the embedding engine to `dashscope` or `ollama` — OneBase will seamlessly bridge them together.

## ☁️ Cloud API Configuration Guide

If you're using cloud models, fill in the corresponding API key in the `.env` file at the project root. You only need to fill in the key for the provider you're using; leave others blank or delete them.

Here are some examples:

```bash
# --- OneBase Environment Variables (.env) ---

# OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxx

# Google
GOOGLE_API_KEY=sk-xxxxxxxxxxxx

# Alibaba Cloud Bailian (DashScope)
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxx

# DeepSeek
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxx

# Zhipu AI
ZHIPU_API_KEY=xxxxxxxxxxxx.xxxxxxxxxxxx

# Baidu Qianfan
QIANFAN_AK=xxxxxxxxxxxx
QIANFAN_SK=xxxxxxxxxxxx
```

## 💻 Local Models

To protect data privacy or save token costs, OneBase provides multiple support options for local computing resources. GPU passthrough for NVIDIA cards is supported via the `--use-gpu` (or `-g`) flag.

### Environment Preparation

1. Ensure the host machine has the latest [NVIDIA](https://www.nvidia.cn/geforce/drivers/) GPU drivers installed with CUDA support. (No need to install CUDA Toolkit — just ensure your GPU driver is up to date.)
2. If running GPU-accelerated inference services inside Docker containers, install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html). (Note: On Windows, install within WSL 2. macOS does not support NVIDIA Container Toolkit.)

---

### Option 1: Ollama (Most Popular, Best for Daily Use)

Ollama is the most popular lightweight local LLM runner. OneBase defaults to Ollama configuration.

- **Host mode (default):** If Ollama is already installed on your system, just run `onebase serve -d`.
- **Container mode:** Run `onebase build --with-ollama -g` and `onebase serve --with-ollama -g -d`. The system will automatically launch an Ollama container and set up network mapping. **Models are auto-pulled on first startup — no manual download needed.**

---

### Option 2: Xinference

Developers often download multi-GB `.safetensors` native weights from ModelScope. Xinference can perfectly manage these local models and expose them as OpenAI-compatible APIs.

- **Host mode (default):**

    Install and run Xinference on the host:
    ```bash
    pip install "xinference[all]"
    xinference-local -H 0.0.0.0 -p 9997
    ```
    Then in OneBase's `onebase.yml`, set `engine` to `openai`, and configure in `.env`: `OPENAI_API_BASE=http://host.docker.internal:9997/v1`.

- **Container mode:** Run `onebase build --with-xinference -g` and `onebase serve --with-xinference -g -d`. The Xinference container will start in the background. **Models are auto-launched based on your `onebase.yml` configuration.** You can also access the `http://localhost:9997` web interface to manage ModelScope models manually.

---

### Option 3: vLLM (High Performance, HuggingFace Compatible)

vLLM is the best framework for maximum inference performance.

- **Host mode (default):** Run on the host:
    ```bash
    python -m vllm.entrypoints.openai.api_server \
    --model <local_model_path_or_HuggingFace_model_ID> \
    --served-model-name my-model \
    --port 9097 \
    --trust-remote-code \
    --tensor-parallel-size 1 \
    --gpu-memory-utilization 0.8
    ```
    Configure in .env: `OPENAI_API_BASE=http://host.docker.internal:9097/v1`

- **Container mode:** Run `onebase build --with-vllm -g` and `onebase serve --with-vllm -g -d`. On startup, the container will automatically read the model ID from `onebase.yml` and download weights for inference! For gated models (Llama, Mistral, etc.), set `HF_TOKEN` in your `.env` file.

---

### Option 4: Docker Model Runner (Simplest, Docker Desktop 4.40+)

Docker Model Runner is the built-in native model manager in Docker Desktop 4.40+. No third-party inference frameworks needed — Docker automatically pulls and manages GGUF quantized models.

```yaml title="onebase.yml"
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

Containers access the OpenAI-compatible API directly at `http://model-runner.docker.internal/engines/llama.cpp/v1` — no API key or port mapping required.

!!! tip "Model Name Format"
    Docker Model Runner uses `ai/` prefixed model names, for example:

    - Reasoning: `ai/qwen2.5:7B-Q4_K_M`, `ai/llama3.2:3B-Q4_K_M`, `ai/deepseek-r1:7B-Q4_K_M`
    - Embedding: `ai/bge-m3:Q4_K_M`, `ai/nomic-embed-text:v1.5-Q4_K_M`

    Use `docker model list` to view locally cached models, or visit [Docker Hub Models](https://hub.docker.com/u/ai) to browse available models.

⚠️ **Recommendation:** Never load model weights directly inside the web service container (this would bloat images to tens of GB and easily cause OOM). The correct approach is to "serve the model as a service". We strongly recommend using Xinference or vLLM to manage your downloaded local models and expose them as APIs that OneBase can consume.
