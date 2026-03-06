<h1 align="center">
  <img src="https://onebase.67656.fun/assets/images/onebase.svg" width="40" height="40" style="vertical-align: middle; margin-right: 10px;" alt="OneBase Logo">
  OneBase AI 模型支持与配置
</h1>

OneBase 秉承“应用层与推理层彻底解耦”的设计理念，通过统一的模型工厂（Model Factory），原生支持全球绝大多数主流云端 API 以及本地大模型推理框架。

## 🌟 支持的云端模型服务商

在 `onebase.yml` 配置文件中，你可以自由组合不同的推理（Reasoning）和向量化（Embedding）引擎：

| 服务商 (Provider)                                             | 标识符 (provider) | 推理引擎 | 向量引擎 | 标准环境变量                                                                                                                            | Base URL                                                                                                 | OpenAI兼容支持 | API参考                                                                                |
| :------------------------------------------------------------ | :---------------- | :------- | :------- | :-------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------- | :------------- | :------------------------------------------------------------------------------------- |
| [OpenAI](https://openai.com)                                  | `openai`          | ✅        | ✅        | `OPENAI_API_KEY`                                                                                                                        | `https://api.openai.com/v1`                                                                              | ✅              | [查看](https://platform.openai.com/docs/api-reference)                                 |
| [Ollama](https://ollama.com) (本地)                           | `ollama`          | ✅        | ✅        | (开箱即用，无需 Key)                                                                                                                    | `http://localhost:11434`                                                                                 | ✅              | [查看](https://docs.ollama.com/api/introduction)                                       |
| [Anthropic / Claude](https://www.anthropic.com)               | `anthropic`       | ✅        | ❌        | `ANTHROPIC_API_KEY`                                                                                                                     | `https://api.anthropic.com/v1`                                                                           | ❌              | [查看](https://docs.anthropic.com/en/api/getting-started)                              |
| [Google Gemini](https://deepmind.google/technologies/gemini/) | `google`          | ✅        | ✅        | `GOOGLE_API_KEY`                                                                                                                        | `https://generativelanguage.googleapis.com/v1beta`                                                       | ✅              | [查看](https://ai.google.dev/gemini-api/docs)                                          |
| [Google Vertex AI](https://cloud.google.com/vertex-ai)        | `google-vertex`   | ✅        | ✅        | `GOOGLE_APPLICATION_CREDENTIALS` (服务账号JSON密钥路径) ；`GOOGLE_CLOUD_PROJECT`(项目ID) ；`VERTEX_LOCATION`：可选，默认为 us-central1  | `https://LOCATION-aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/LOCATION/publishers/google` | ⚠️              | [查看](https://cloud.google.com/vertex-ai/docs/reference)                              |
| [Groq](https://groq.com)                                      | `groq`            | ✅        | ❌        | `GROQ_API_KEY`                                                                                                                          | `https://api.groq.com/openai/v1`                                                                         | ✅              | [查看](https://console.groq.com/docs/api-reference)                                    |
| [阿里云百炼 / 通义](https://www.aliyun.com/product/bailian)   | `dashscope`       | ✅        | ✅        | `DASHSCOPE_API_KEY`                                                                                                                     | `https://dashscope.aliyuncs.com/compatible-mode/v1`                                                      | ✅              | [查看](https://help.aliyun.com/model-studio/get-api-key)                               |
| [智谱 AI / GLM](https://www.zhipuai.cn)                       | `zhipu`           | ✅        | ✅        | `ZHIPU_API_KEY`                                                                                                                         | `https://open.bigmodel.cn/api/paas/v4`                                                                   | ✅              | [查看](https://docs.bigmodel.cn/cn/api)                                                |
| [魔搭社区 (ModelScope)](https://www.modelscope.cn)            | `modelscope`      | ✅        | ✅        | `MODELSCOPE_SDK_TOKEN` (在线调用)                                                                                                       | `https://api.modelscope.cn/v1`                                                                           | ❌              | [查看](https://www.modelscope.cn/docs)                                                 |
| [百度千帆](https://cloud.baidu.com/product/wenxinworkshop)    | `qianfan`         | ✅        | ✅        | `QIANFAN_AK` & `QIANFAN_SK`                                                                                                             | `https://qianfan.baidubce.com/v2`                                                                        | ✅              | [查看](https://cloud.baidu.com/doc/WENXINWORKSHOP/index.html)                          |
| [DeepSeek](https://www.deepseek.com)                          | `deepseek`        | ✅        | ❌        | `DEEPSEEK_API_KEY`                                                                                                                      | `https://api.deepseek.com/v1`                                                                            | ✅              | [查看](https://platform.deepseek.com/api-docs/)                                        |
| [字节跳动豆包](https://www.volcengine.com/product/doubao)     | `doubao`          | ✅        | ✅        | `VOLC_ACCESS_KEY`（火山引擎的Access Key） `VOLC_SECRET_KEY`（）（火山引擎的Secret Key） `VOLC_ENGINE_ENDPOINT_ID`（火山方舟的接入点ID） | `https://ark.cn-beijing.volces.com/api/v3`                                                               | ✅              | [查看](https://www.volcengine.com/docs/82379/1541594)                                  |
| [SiliconFlow (硅基流动)](https://siliconflow.cn)              | `siliconflow`     | ✅        | ✅        | `SILICONFLOW_API_KEY`                                                                                                                   | `https://api.siliconflow.cn/v1`                                                                          | ✅              | [查看](https://docs.siliconflow.cn/cn/api-reference/chat-completions/chat-completions) |

⚠️ **注意：** Google Vertex需要将服务账号JSON密钥路径挂载到容器内，可能需要手动调整代码！

💡 **提示：** 你可以将推理引擎设置为 `deepseek`，而将向量引擎设置为 `dashscope` 或 `ollama`，OneBase 会完美地将它们桥接在一起。

## ☁️ 云端 API 配置指南

如果你使用的是云端模型，请在项目根目录的 `.env` 文件中填入相应的 API Key。你只需要填写你正在使用的服务商 Key，其他的可以留空或删除。
以下是一些示例：
```bash
# --- OneBase 环境变量配置文件 (.env) ---

# OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxx

# Google
GOOGLE_API_KEY=sk-xxxxxxxxxxxx

# 阿里云百炼 (DashScope)
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxx

# DeepSeek
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxx

# 智谱 AI
ZHIPU_API_KEY=xxxxxxxxxxxx.xxxxxxxxxxxx

# 百度千帆
QIANFAN_AK=xxxxxxxxxxxx
QIANFAN_SK=xxxxxxxxxxxx
```

## 💻 本地模型
为了保障数据隐私或节省 Token 成本，OneBase 对本地算力提供了多种的支持方案。并支持通过 `--use-gpu` (或 `-g`) 参数一键直通物理机 NVIDIA 显卡。
### 环境准备
1. 请确保宿主机已经安装好 [NVIDIA]((https://www.nvidia.cn/geforce/drivers/)) 显卡驱动，并且支持 CUDA。(无需安装CUDA Toolkit，仅需确保你的显卡驱动已是最新) 
2. 如果选择在 Docker 容器内运行 GPU 加速的推理服务，需要安装[Nvidia Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)（注意，如果是Windows，需要在wsl2上安装，macOS不支持Nvidia Container Toolkit）
---

### 方案一：使用 Ollama (最流行，适合日常使用)

Ollama 是目前最流行的轻量级本地大模型运行器。OneBase 默认配置即为 Ollama。

-   **宿主机模式（默认）：** 若系统已安装 Ollama，直接执行 `onebase serve -d`。
-   **纯容器模式：** 执行`onebase build --with-ollama -g` 和 `onebase serve --with-ollama -g -d`，系统将自动拉起 Ollama 容器，并打通网络映射。**模型会在首次启动时自动拉取，无需手动下载。**

---

### 方案二：使用 Xinference 

开发者常从modelscope社区下载几十GB的 `.safetensors` 原生权重。Xinference 能完美接管这些本地模型，并转化为 OpenAI 兼容的 API。

-   **宿主机模式（默认）：** 
  
    在宿主机安装并运行Xinference :
    ```bash
    pip install "xinference[all]"
    xinference-local -H 0.0.0.0 -p 9997
    ```
    然后在 OneBase 的 `onebase.yml` 将 `engine` 设为 `openai`，并在 `.env` 配置：`OPENAI_API_BASE=http://host.docker.internal:9997/v1`。
-   **纯容器模式：** 执行`onebase build --with-xinference -g` 和 `onebase serve --with-xinference -g -d`。Xinference 容器将在后台启动，**模型会根据 `onebase.yml` 配置自动启动。**你也可以访问 `http://localhost:9997` 的 Web 界面手动管理 ModelScope 的模型。

---

### 方案三：使用 vLLM (性能强大，兼容HuggingFace)

vLLM 是追求极致推理性能的最佳框架。

-   **宿主机模式（默认）：** 在宿主机执行:
-   ```bash
    python -m vllm.entrypoints.openai.api_server \
    --model <本地模型路径或HuggingFace模型ID> \
    --served-model-name my-model \
    --port 9097 \ # 注意，避开后端FastAPI的默认端口
    --trust-remote-code \
    --tensor-parallel-size 1 \
    --gpu-memory-utilization 0.8
    ```
    在.env中配置：`OPENAI_API_BASE=http://host.docker.internal:9097/v1`

-   **纯容器模式：** 执行`onebase build --with-vllm -g` 和 `onebase serve --with-vllm -g -d`。容器启动时，将自动读取 `onebase.yml` 中的大模型 ID 并自动下载权重执行推理！对于需要授权的模型（如 Llama、Mistral 等），请在 `.env` 中设置 `HF_TOKEN`。

---

### 方案四：使用 Docker Model Runner（最简单，Docker Desktop 4.40+）

Docker Model Runner 是 Docker Desktop 4.40+ 内置的原生模型管理器，无需安装任何第三方推理框架，Docker 自动拉取和管理 GGUF 量化模型。

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

容器内直接通过 `http://model-runner.docker.internal/engines/llama.cpp/v1` 访问 OpenAI 兼容 API，无需任何 API Key 或端口映射。

!!! tip "模型名称格式"
    Docker Model Runner 使用 `ai/` 前缀的模型名称，例如：

    - 推理：`ai/qwen2.5:7B-Q4_K_M`、`ai/llama3.2:3B-Q4_K_M`、`ai/deepseek-r1:7B-Q4_K_M`
    - 向量化：`ai/bge-m3:Q4_K_M`、`ai/nomic-embed-text:v1.5-Q4_K_M`

    可通过 `docker model list` 查看本地已缓存的模型，或访问 [Docker Hub Models](https://hub.docker.com/u/ai) 浏览可用模型。

### 其他可行性
理论上所有本地的OpenAI兼容接口都可以用于`onebase`，如`OpenClaw`、`LM studio`等，但需了解具体的接口URL，并在onebase.yml中配置服务商为`openai`，在.env中填写OPENAI_BASE_URL为你的本地借口名称，并确保模型名称正确。

!!! warning "注意"
    onebase不确保兼容所有未列出的本地API接口！

---

!!! tip "⚠️ **建议：**"
    永远不要在 Web 服务容器内直接加载模型权重（这会导致镜像暴涨至几十G，且极易导致显存溢出）。正确的做法是将 模型“推理服务化”。我们强烈推荐使用 Xinference 或 vLLM 来接管你下载的本地模型，并将其转化为 OneBase 可用的 API 接口。