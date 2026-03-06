# 快速入门

本指南将带你从零开始，用 OneBase 搭建一个属于自己的 AI 知识库问答系统。

---

## 环境要求

在开始之前，请确保你的系统满足以下条件：

| 依赖                                                                                                                       | 最低版本 | 说明                                  |
| :------------------------------------------------------------------------------------------------------------------------- | :------- | :------------------------------------ |
| [Python](https://www.python.org/downloads/)                                                                                | 3.10+    | OneBase CLI 运行环境                  |
| [Docker Desktop](https://www.docker.com/products/docker-desktop/)/[Docker Engine + Compose](https://docs.docker.com/engine/install/) | 20.10+   | 容器化部署后端、数据库等服务          |
| pip                                                                                                                        | 22.0+    | Python 包管理器（通常随 Python 安装） |

<div class="ob-note-grid">
  <div class="ob-note">推荐使用最新稳定版 Python，并确保已配置好系统 PATH。</div>
  <div class="ob-note">本地 GPU 加速可显著提升推理速度。</div>
</div>

!!! tip "Windows 用户提示"
    请确保 Docker Desktop 已启用 WSL 2 后端，并在系统 PATH 中包含 `docker` 和 `python` 命令。

---

!!! tip "容器环境下使用本机 GPU 加速（仅针对使用`--with`参数的情况）"
    如需在容器环境中使用 GPU 加速推理，还需安装 [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) 并确认 `docker run --gpus all nvidia/cuda:12.0-base nvidia-smi` 正常输出。

---


<div class="ob-section">
  <h2>⚡快速上手路线</h2>
  <ol class="ob-steps">
    <li>安装 CLI 并验证版本。</li>
    <li>初始化项目并配置模型。</li>
    <li>构建知识库并启动服务。</li>
  </ol>
</div>

## 安装 OneBase

通过 pip 全局安装 OneBase CLI：

```bash
pip install onebase-ai
```

安装完成后，验证是否安装成功：

```bash
onebase --version
```

你应该看到类似以下的输出：

```
OneBase CLI, version 0.1.2
```

---

## 初始化项目

在一个空目录下执行 `init` 命令，OneBase 会为你生成一整套项目脚手架：

```bash
mkdir my-knowledge-base
cd my-knowledge-base
onebase init
```

初始化完成后，你的项目结构如下：

```
my-knowledge-base/
├── .env                # API 密钥与数据库凭据（自动生成安全密码）
├── onebase.yml         # 核心配置文件
├── requirements.txt    # 动态依赖清单（待生成）
└── base/               # 知识库文档目录
    └── overview.md     # 示例文档
```

---

## 配置模型

OneBase 支持[多种云端与本地模型](user-guide/config/MODELS.md)。你需要编辑两个文件来完成模型配置。

### 1. 选择模型引擎

编辑 `onebase.yml`，设置推理（Reasoning）和向量化（Embedding）引擎：

```yaml title="onebase.yml"
site_name: My AI Assistant

engine:
  reasoning:
    provider: openai          # 支持 openai / ollama / deepseek / dashscope 等
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
  struct: default             # 自动扫描 base/ 目录结构

features:
  chat_history: true          # 多轮对话记忆
  file_upload: true           # 前端实时文档上传
```

### 2. 填写 API 密钥

编辑 `.env` 文件，填入你使用的模型服务商的 API Key：

```bash title=".env"
# 只需填写你实际使用的服务商
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxx
```

!!! note "使用本地模型？（无需 API Key）"
    **方式一：Ollama（推荐）**

    如果你选择 Ollama 作为引擎，请确保宿主机已安装并启动了 [Ollama](https://ollama.com)，或使用 `--with-ollama` 参数让 OneBase 自动启动 Ollama 容器（模型会自动拉取）。无需填写任何 API Key。

    **方式二：Docker Model Runner（Docker Desktop 4.40+）**

    如果你使用的是 Docker Desktop 4.40+，可以直接使用 Docker 原生模型管理器，无需安装任何第三方工具：

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

    Docker 会自动管理模型的拉取和运行，无需任何 API Key。

    **方式三：Xinference / vLLM（OpenAI 兼容方案）**

    在 `onebase.yml` 中将 provider 设为 `openai`：

    ```yaml
    engine:
      reasoning:
        provider: openai
        model: qwen-1.8b
    ```

    在 `.env` 中填写本地服务的 API 地址。**直接写 `localhost` 即可**——OneBase 会在容器内自动将其重写为 `host.docker.internal`：

    ```bash
    OPENAI_BASE_URL=http://localhost:9997/v1
    ```

    你也可以使用 `--with-xinference` 或 `--with-vllm` 参数让 OneBase 自动启动对应容器，此时无需手动配置 URL。


---

## 准备知识库文档

将你的文档文件放入 `base/` 目录。支持以下格式：

- **Markdown** (`.md`) — 推荐，支持前端可视化预览
- **PDF** (`.pdf`) — 自动提取文本内容
- **纯文本** (`.txt`) — 自动检测编码

你可以使用子目录来组织内容，OneBase 会自动生成对应的导航树：

```
base/
├── overview.md
├── 开发指南/
│   ├── 快速入门.md
│   └── API接口.md
└── 产品文档/
    ├── 设计规范.pdf
    └── 常见问题.txt
```

---

## 安装依赖

OneBase 会根据你在 `onebase.yml` 中选择的模型引擎，自动计算所需的 Python 依赖包：

```bash
# 生成依赖清单并写入 requirements.txt
onebase get-deps > requirements.txt

# 安装依赖
pip install -r requirements.txt
```

---

## 构建知识库

一切就绪后，执行 `build` 命令。OneBase 将自动完成以下流程：

1. 启动 PostgreSQL + pgvector 数据库容器
2. 扫描并读取 `base/` 目录下的所有文档
3. 将文档切分为语义块（Chunk）
4. 调用 Embedding API 生成向量并写入数据库

```bash
onebase build
```

输出示例：

```
📦 Reading config onebase.yml...
✔ Config loaded successfully!
🔍 Scanning knowledge base directory...
✂️ Chunking documents (Chunk Size: 500)...
✔ Done! Generated 128 memory chunks.
💾 Starting backend services and writing data...
✔ Successfully wrote 128 vectors to the database!
```

---

## 启动服务

构建完成后，启动全栈服务（后端 API + 前端 UI）：

```bash
# 后台运行（推荐）
onebase serve -d

# 或 指定端口
onebase serve --port 3000 -d
```

启动成功后，在浏览器中打开 [http://localhost:8000](http://localhost:8000)，你将看到 OneBase 的聊天界面：

- **左侧边栏**：知识库文件树，点击可预览 Markdown 文档
- **中央区域**：AI 对话窗口，支持多轮问答
- **输入框**：输入问题后按 Enter 发送，Shift+Enter 换行

---

## 停止服务

```bash
# 停止所有容器
onebase stop

# 停止并清除数据卷（⚠️ 将删除数据库数据）
onebase stop -v
```

---

## 使用本地 GPU 加速

如果你有 NVIDIA 显卡，可以通过 `--use-gpu` (`-g`) 参数启用 GPU 直通：

```bash
# 使用 Ollama 容器 + GPU
onebase build --with-ollama -g
onebase serve --with-ollama -g -d
```

!!! warning "GPU 环境要求"
    1. 宿主机已安装最新 [NVIDIA 显卡驱动](https://www.nvidia.cn/geforce/drivers/)
    2. 已安装 [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)（Windows 需在 WSL 2 中安装）

---

## 常用命令速查

| 命令                                | 说明                           |
| :---------------------------------- | :----------------------------- |
| `onebase init`                      | 初始化项目脚手架               |
| `onebase init --force`              | 强制重新初始化（覆盖已有文件） |
| `onebase get-deps`                  | 输出当前配置所需的依赖包       |
| `onebase build`                     | 构建向量知识库                 |
| `onebase build --with-ollama -g`    | 使用 Ollama 容器 + GPU 构建    |
| `onebase build --with-docker-model` | 使用 Docker 原生模型构建       |
| `onebase serve -d`                  | 后台启动全栈服务               |
| `onebase serve -p 3000 -d`          | 指定端口启动                   |
| `onebase stop`                      | 停止所有服务                   |
| `onebase stop -v`                   | 停止并删除数据卷               |
| `onebase --lang zh`                 | 切换 CLI 输出为中文            |
| `onebase -h`                        | 查看帮助                       |

---

## 下一步

- 📖 阅读 [模型支持与配置](user-guide/config/MODELS.md)，了解所有可用的模型引擎
- 🔧 深入 [配置](user-guide/config/engine.md)，掌握 `onebase.yml` 的全部选项
- 💻 了解 [OneBase CLI的全部命令和参数](user-guide/cli/basic.md) 来掌握 OneBase 的功能