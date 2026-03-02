# 基本命令

OneBase CLI 提供 5 个核心命令，覆盖项目从初始化到停止的完整生命周期。

---

## 命令总览

```bash
onebase [全局选项] <命令> [命令选项]
```

| 命令       | 说明                       | 前置条件                      |
| :--------- | :------------------------- | :---------------------------- |
| `init`     | 初始化项目结构和配置文件   | 无                            |
| `get-deps` | 检测并输出所需 Python 依赖 | `onebase.yml`                 |
| `build`    | 构建向量知识库             | `onebase.yml` + 文档 + Docker |
| `serve`    | 启动完整服务栈             | `onebase.yml` + Docker        |
| `stop`     | 停止并移除容器             | 运行中的服务                  |

---

## init — 初始化项目

创建一个新的 OneBase 项目，生成所有必要的配置文件。

```bash
onebase init
onebase init --force   # 覆盖已有文件
```

生成的文件和目录：

| 文件/目录          | 内容                                       |
| :----------------- | :----------------------------------------- |
| `onebase.yml`      | 站点配置（引擎、数据库、知识库、功能开关） |
| `.env`             | 数据库凭据（随机密码）+ API 密钥模板       |
| `base/`            | 知识库文档目录，包含 `overview.md` 示例    |
| `.onebase/`        | 运行时缓存目录                             |
| `requirements.txt` | 依赖清单模板                               |

### 典型流程

```bash
mkdir my-ai-site && cd my-ai-site
onebase init
# 编辑 onebase.yml 和 .env
onebase get-deps > requirements.txt
pip install -r requirements.txt
```

!!! tip "安全设计"
    `.env` 中的 `POSTGRES_PASSWORD` 使用 `secrets.token_urlsafe(16)` 自动生成，128 位加密安全随机密码。

---

## get-deps — 检测依赖

根据 `onebase.yml` 中配置的 provider 和功能，自动计算所需的 Python 包列表。

```bash
onebase get-deps                     # 输出到终端
onebase get-deps > requirements.txt  # 重定向写入文件
```

输出示例：

```
langchain-ollama>=0.2.0
langchain-community>=0.3.0
psycopg[binary]>=3.1
```

!!! info "为什么需要这一步？"
    OneBase 本体只包含核心逻辑，推理 SDK（如 `langchain-openai`、`langchain-ollama`）按需安装。`get-deps` 根据你选择的 provider 精确输出依赖，避免安装不需要的包。

---

## build — 构建知识库

解析文档、切块生成向量、写入数据库。这是知识库从原始文档到可检索状态的关键步骤。

```bash
onebase build
onebase build --with-ollama
onebase build --with-ollama --use-gpu
```

### 执行流程

```
解析 onebase.yml
     ↓
扫描 base/ 目录（MD/PDF/TXT）
     ↓
文档切块（按 chunk_size）
     ↓
启动 Docker 容器（db + 可选推理引擎）
     ↓
等待 PostgreSQL 就绪（最长 30s）
     ↓
向量化 & 写入 pgvector
```

### 使用场景

| 场景                | 命令                              |
| :------------------ | :-------------------------------- |
| 宿主机已安装 Ollama | `onebase build`                   |
| 使用容器化 Ollama   | `onebase build --with-ollama`     |
| GPU 加速嵌入        | `onebase build --with-ollama -g`  |
| 使用 Xinference     | `onebase build --with-xinference` |
| 使用 vLLM     | `onebase build --with-vllm`         |

!!! warning "推理引擎互斥"
    `--with-ollama`、`--with-xinference`、`--with-vllm` 三者只能同时指定一个，否则报错退出。

!!! note "首次使用容器化模型"
    如果容器内模型权重尚未下载，向量入库可能失败。建议先通过 `onebase serve --with-ollama -d` 启动容器并手动拉取模型，再运行 `build`。

---

## serve — 启动服务

启动完整服务栈：后端 API + 数据库 + 前端 UI + 可选推理引擎。

```bash
onebase serve              # 前台运行
onebase serve -d           # 后台运行
onebase serve -d -p 3000   # 后台运行，端口 3000
onebase serve --with-ollama -d   # 附带 Ollama 容器
```

### 启动流程

```
解析 onebase.yml
     ↓
尝试拉取预构建镜像（超时 15s）
  ├─ 成功 → 使用远程镜像
  └─ 失败 → 本地构建镜像
     ↓
生成 docker-compose.yml
     ↓
docker compose up [-d] [--build]
     ↓
输出访问地址和状态面板
```

### 启动后输出

后台模式（`-d`）启动成功后显示状态面板：

```
╭─── Status: Online ───╮
│ 🎉 OneBase is running!                           │
│                                                    │
│ 🌐 URL: http://localhost:8000                      │
│ 🛑 Stop: run onebase stop                          │
╰────────────────────────────────────────────────────╯
```

前台模式会实时输出容器日志，按 `Ctrl+C` 停止。

---

## stop — 停止服务

停止所有运行中的 OneBase 容器并清理网络。

```bash
onebase stop       # 停止容器，保留数据
onebase stop -v    # 停止容器并清除数据卷
```

!!! danger "`-v` 操作不可恢复"
    使用 `--volumes` 会永久删除：

    - PostgreSQL 数据库（所有向量数据）
    - 本地模型缓存（Ollama / Xinference / vLLM 权重）

    删除后需重新 `build` 构建知识库，容器化模型需重新下载。

---

## 全局选项

这些选项在**任何命令之前**使用，影响全局行为。

```bash
onebase --version          # 显示版本号
onebase --lang zh build    # 中文输出
onebase --verbose serve -d # 调试模式
onebase --quiet build      # 静默模式（仅错误）
```

| 选项        | 缩写 | 说明                         |
| :---------- | :--- | :--------------------------- |
| `--version` | `-V` | 显示版本号并退出             |
| `--lang`    | `-l` | 输出语言：`en`（默认）、`zh` |
| `--verbose` | `-v` | 调试模式，输出详细日志       |
| `--quiet`   | `-q` | 静默模式，仅显示错误         |
| `--help`    | `-h` | 显示帮助信息                 |

!!! tip "持久化语言设置"
    设置环境变量 `ONEBASE_LANG=zh` 可避免每次输入 `--lang zh`。

---

## 相关文档

- [参数详解](args.md) — 每个选项的完整说明与用例
- [本地部署](../deploy/cloud_deploy.md) — 端到端部署指南
- [预设配置](../config/preset_config.md) — 常见场景配置模板
