# 参数详解

OneBase CLI 全部选项的完整说明、取值范围与组合用例。

---

## 全局选项

全局选项写在命令名**之前**，对所有命令生效。

### `--version` / `-V`

显示 OneBase 版本号并立即退出。版本号从 `pyproject.toml` 元数据中读取。

```bash
onebase -V
# OneBase CLI, version 0.1.2
```

| 属性   | 值                               |
| :----- | :------------------------------- |
| 类型   | `bool`（标志位）                 |
| 默认值 | `False`                          |
| 优先级 | Eager — 出现即执行，忽略后续参数 |

---

### `--lang` / `-l`

设置 CLI 输出语言。影响所有日志、提示、错误信息的显示语言。

```bash
onebase --lang zh build     # 中文输出
onebase -l en serve -d      # 英文输出
```

| 属性   | 值                         |
| :----- | :------------------------- |
| 类型   | `str`                      |
| 默认值 | `en`                       |
| 可选值 | `en`（英文）、`zh`（中文） |

**环境变量替代：**

```bash
export ONEBASE_LANG=zh   # Linux/macOS
set ONEBASE_LANG=zh      # Windows CMD
$env:ONEBASE_LANG="zh"   # PowerShell
```

设置后无需每次传入 `--lang`，命令行参数优先级高于环境变量。

---

### `--verbose` / `-v`

启用调试模式，输出 DEBUG 级别日志。包含容器启动命令、数据库连接探测、内部状态等。

```bash
onebase -v build
# PG ready (attempt 1)
# Starting container group: db
# Executing: docker compose -f .onebase/docker-compose.yml up -d db
```

| 属性     | 值      |
| :------- | :------ |
| 类型     | `bool`  |
| 默认值   | `False` |
| 日志级别 | `DEBUG` |

---

### `--quiet` / `-q`

静默模式，仅输出 ERROR 级别日志。适用于 CI/CD 管道或脚本中调用。

```bash
onebase -q build && echo "success"
```

| 属性     | 值      |
| :------- | :------ |
| 类型     | `bool`  |
| 默认值   | `False` |
| 日志级别 | `ERROR` |

!!! note "`--verbose` 和 `--quiet` 互斥"
    同时传入时 `--quiet` 优先（ERROR 级别覆盖 DEBUG 级别）。

---

### `--help` / `-h`

显示帮助信息。可用于主命令或子命令。

```bash
onebase -h          # 显示全局帮助
onebase build -h    # 显示 build 命令帮助
onebase serve -h    # 显示 serve 命令帮助
```

---

## init 选项

### `--force` / `-f`

覆盖已有的配置文件。默认情况下，如果 `onebase.yml` 已存在则拒绝执行并退出。

```bash
onebase init --force
```

| 属性   | 值      |
| :----- | :------ |
| 类型   | `bool`  |
| 默认值 | `False` |

**覆盖范围：**

| 文件               | `--force` 行为             |
| :----------------- | :------------------------- |
| `onebase.yml`      | 重新生成默认配置           |
| `.env`             | 重新生成（**新随机密码**） |
| `requirements.txt` | 重新生成模板               |
| `base/overview.md` | 重新生成                   |

!!! warning "密码将被重置"
    `--force` 会生成新的 `POSTGRES_PASSWORD`。如果已有数据库在运行，需先 `onebase stop -v` 清除旧数据卷，否则新密码无法连接旧数据库。

---

## get-deps 选项

`get-deps` 没有专属选项。它读取 `onebase.yml` 并将依赖列表输出到 stdout。

```bash
# 标准用法：重定向到文件
onebase get-deps > requirements.txt
pip install -r requirements.txt
```

**输出格式：** 每行一个包名（含版本约束），符合 pip requirements 格式。

**依赖映射逻辑：** 根据 `engine.reasoning.provider` 和 `engine.embedding.provider` 映射对应的 SDK 包。例如：

| provider    | 生成的依赖                                     |
| :---------- | :--------------------------------------------- |
| `ollama`    | `langchain-ollama>=0.2.0`                      |
| `openai`    | `langchain-openai>=0.2.0`                      |
| `dashscope` | `langchain-community>=0.3.0`, `dashscope>=1.0` |

---

## build 选项

### `--with-ollama`

随 `build` 一同启动 Ollama Docker 容器，用于容器内嵌入计算。

```bash
onebase build --with-ollama
```

| 属性     | 值               |
| :------- | :--------------- |
| 类型     | `bool`           |
| 默认值   | `False`          |
| 容器名   | `onebase_ollama` |
| 暴露端口 | `11434`          |

**效果：** 在 `docker compose up` 时除 `db` 外额外启动 `ollama` 服务，并将 `OLLAMA_BASE_URL` 设为 `http://ollama:11434`（Docker 内部网络）。

---

### `--with-xinference`

启动 Xinference 容器（ModelScope 生态）。

```bash
onebase build --with-xinference
```

| 属性     | 值                      |
| :------- | :---------------------- |
| 类型     | `bool`                  |
| 默认值   | `False`                 |
| 容器名   | `onebase_xinference`    |
| 暴露端口 | `9997`                  |
| 管理界面 | `http://localhost:9997` |

**效果：** 将 `OPENAI_API_BASE` 覆盖为 `http://xinference:9997/v1`（OpenAI 兼容协议）。

---

### `--with-vllm`

启动 vLLM 容器（高吞吐推理）。

```bash
onebase build --with-vllm --use-gpu
```

| 属性     | 值                      |
| :------- | :---------------------- |
| 类型     | `bool`                  |
| 默认值   | `False`                 |
| 容器名   | `onebase_vllm`          |
| 暴露端口 | `8001`（映射内部 8000） |

**效果：** 从 `onebase.yml` 读取 `engine.reasoning.model` 传给 vLLM 的 `--model` 参数，并将 `OPENAI_API_BASE` 覆盖为 `http://vllm:8000/v1`。

---

### `--use-gpu` / `-g`

为容器化推理引擎启用 NVIDIA GPU 直通。

```bash
onebase build --with-ollama -g
```

| 属性     | 值                              |
| :------- | :------------------------------ |
| 类型     | `bool`                          |
| 默认值   | `False`                         |
| 前置条件 | NVIDIA Container Toolkit 已安装 |

**生成的 Compose 配置：**

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

!!! note "仅对推理容器生效"
    `-g` 只影响 `--with-ollama`、`--with-xinference`、`--with-vllm` 启动的推理容器，不影响数据库或后端容器。未指定任何推理引擎时 `-g` 无实际效果。

---

### 推理引擎互斥规则

`--with-ollama`、`--with-xinference`、`--with-vllm` 三者**至多选一**：

```bash
# ✅ 合法
onebase build
onebase build --with-ollama
onebase build --with-vllm -g

# ❌ 非法 — 同时指定多个引擎
onebase build --with-ollama --with-xinference
# → ❌ Container conflict: only one local inference engine can be specified at a time.
```

---

## serve 选项

`serve` 包含 `build` 的全部推理引擎选项，另外新增 `--port` 和 `--detach`。

### `--port` / `-p`

指定服务绑定的宿主机端口。

```bash
onebase serve -d -p 3000
```

| 属性   | 值                            |
| :----- | :---------------------------- |
| 类型   | `int`                         |
| 默认值 | `8000`                        |
| 映射   | 宿主机 `port` → 容器内 `8000` |

---

### `--detach` / `-d`

后台运行容器（Docker detached 模式）。

```bash
onebase serve -d    # 后台启动，立即返回终端
onebase serve       # 前台启动，Ctrl+C 停止
```

| 属性   | 值      |
| :----- | :------ |
| 类型   | `bool`  |
| 默认值 | `False` |

**行为差异：**

| 模式         | 日志           | 终端控制 | 停止方式       |
| :----------- | :------------- | :------- | :------------- |
| 前台（默认） | 实时输出到终端 | 阻塞     | `Ctrl+C`       |
| 后台 (`-d`)  | 不输出         | 立即返回 | `onebase stop` |

---

### `--with-ollama` / `--with-xinference` / `--with-vllm` / `--use-gpu`

与 `build` 命令完全相同，参见上方说明。互斥规则同样适用。

---

## stop 选项

### `--volumes` / `-v`

停止容器时同时删除 Docker 数据卷。

```bash
onebase stop       # 保留数据
onebase stop -v    # 删除数据卷
```

| 属性   | 值      |
| :----- | :------ |
| 类型   | `bool`  |
| 默认值 | `False` |

**删除的数据卷：**

| 数据卷            | 内容                  | 影响                             |
| :---------------- | :-------------------- | :------------------------------- |
| `pgdata`          | PostgreSQL 数据库     | 向量数据全部丢失，需重新 `build` |
| `ollama_data`     | Ollama 模型缓存       | 需重新 `ollama pull`             |
| `xinference_data` | Xinference 模型缓存   | 需重新下载模型                   |
| `vllm_data`       | vLLM HuggingFace 缓存 | 需重新下载权重                   |

---

## 选项速查表

| 命令    | 选项                | 缩写 | 类型 | 默认值  |
| :------ | :------------------ | :--- | :--- | :------ |
| 全局    | `--version`         | `-V` | flag | —       |
| 全局    | `--lang`            | `-l` | str  | `en`    |
| 全局    | `--verbose`         | `-v` | flag | `False` |
| 全局    | `--quiet`           | `-q` | flag | `False` |
| `init`  | `--force`           | `-f` | flag | `False` |
| `build` | `--with-ollama`     | —    | flag | `False` |
| `build` | `--with-xinference` | —    | flag | `False` |
| `build` | `--with-vllm`       | —    | flag | `False` |
| `build` | `--use-gpu`         | `-g` | flag | `False` |
| `serve` | `--port`            | `-p` | int  | `8000`  |
| `serve` | `--detach`          | `-d` | flag | `False` |
| `serve` | `--with-ollama`     | —    | flag | `False` |
| `serve` | `--with-xinference` | —    | flag | `False` |
| `serve` | `--with-vllm`       | —    | flag | `False` |
| `serve` | `--use-gpu`         | `-g` | flag | `False` |
| `stop`  | `--volumes`         | `-v` | flag | `False` |

---

## 组合用例

### 零配置本地体验

```bash
onebase init
onebase get-deps > requirements.txt && pip install -r requirements.txt
# 确保宿主机已运行 Ollama 并拉取了模型
onebase build
onebase serve -d
```

### 全容器化 + GPU

```bash
onebase init
onebase build --with-ollama -g
onebase serve --with-ollama -g -d -p 80
```

### CI/CD 管道

```bash
onebase -q build && onebase -q serve -d
```

### 中文输出 + 调试

```bash
onebase --lang zh -v build --with-ollama
```

### 重置项目

```bash
onebase stop -v        # 清除容器和数据
onebase init --force   # 重新生成配置
onebase build          # 重新构建
```

---

## 相关文档

- [基本命令](basic.md) — 命令概览与执行流程
- [原地部署](../deploy/cloud_deploy.md) — 完整部署指南
- [引擎配置](../config/engine.md) — provider 与模型选择
