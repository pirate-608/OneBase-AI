OneBase采取约定大于配置的策略提供知识库定制的解决方案，通过读取一份核心文件`onebase.yml`来导入所有用户自定义的配置信息，通过.env文件将敏感信息添加到环境变量，并将这些配置和环境变量注入服务运行时。填写`onebase.yml`时，必须遵守特定的规范格式。
以下是一份完整配置示例：

```yaml title="onebase.yml"
# ---- 站点名称（必填）----
site_name: My AI Assistant

# ---- 引擎配置（必填）----
engine:
  reasoning:                    # 推理引擎
    provider: ollama            # 服务商标识符
    model: deepseek-r1:1.5b     # 模型名称
  embedding:                    # 向量引擎
    provider: ollama
    model: nomic-embed-text:v1.5

# ---- 数据库配置 ----
database:
  type: postgresql              # 仅支持 postgresql
  vector_store: pgvector        # 仅支持 pgvector

# ---- 知识库配置 ----
knowledge_base:
  path: ./base                  # 文档根目录
  chunk_size: 500               # 切块大小（字符数），必须 > 0
  struct: default               # 目录结构：default 或手动指定

# ---- 功能开关 ----
features:
  chat_history: true            # 多轮对话历史记录
  file_upload: true             # 前端实时文档上传
```

## 配置字段速查表

| 字段                        | 类型           | 必填  | 默认值       | 说明                                            |
| :-------------------------- | :------------- | :---: | :----------- | :---------------------------------------------- |
| `site_name`                 | string         |   ✅   | —            | 站点名称，显示在前端标题栏                      |
| `engine.reasoning.provider` | string         |   ✅   | —            | 推理引擎服务商，见[引擎配置](engine.md)         |
| `engine.reasoning.model`    | string         |   ✅   | —            | 推理模型名称                                    |
| `engine.embedding.provider` | string         |   ✅   | —            | 向量引擎服务商                                  |
| `engine.embedding.model`    | string         |   ✅   | —            | 向量模型名称                                    |
| `database.type`             | Literal        |   —   | `postgresql` | 数据库类型，当前仅支持 `postgresql`             |
| `database.vector_store`     | Literal        |   —   | `pgvector`   | 向量存储引擎，当前仅支持 `pgvector`             |
| `knowledge_base.path`       | string         |   —   | `./base`     | 知识库文档根目录路径                            |
| `knowledge_base.chunk_size` | int            |   —   | `500`        | 文本切块大小，必须大于 0                        |
| `knowledge_base.struct`     | string \| dict |   —   | `default`    | 目录结构映射，见[知识库配置](knowledge_base.md) |
| `features.chat_history`     | bool           |   —   | `true`       | 启用对话历史记录                                |
| `features.file_upload`      | bool           |   —   | `true`       | 启用前端文件上传                                |

---

## 环境变量速查表（.env）

| 变量名                      | 用途                | 必填  | 说明                             |
| :-------------------------- | :------------------ | :---: | :------------------------------- |
| `POSTGRES_USER`             | 数据库用户名        |   —   | 默认 `onebase`                   |
| `POSTGRES_PASSWORD`         | 数据库密码          |   ✅   | `onebase init` 自动生成          |
| `POSTGRES_DB`               | 数据库名            |   —   | 默认 `onebase_db`                |
| `POSTGRES_HOST`             | 数据库主机          |   —   | 默认 `localhost`                 |
| `POSTGRES_PORT`             | 数据库端口          |   —   | 默认 `5432`                      |
| `OPENAI_API_KEY`            | OpenAI API 密钥     |   ⚡   | provider 为 `openai` 时必填      |
| `OPENAI_BASE_URL`           | OpenAI 兼容接口地址 |   —   | 本地推理框架时填写               |
| `OLLAMA_BASE_URL`           | Ollama 服务地址     |   —   | 默认 `http://localhost:11434`    |
| `DASHSCOPE_API_KEY`         | 阿里云百炼密钥      |   ⚡   | provider 为 `dashscope` 时必填   |
| `DEEPSEEK_API_KEY`          | DeepSeek 密钥       |   ⚡   | provider 为 `deepseek` 时必填    |
| `ANTHROPIC_API_KEY`         | Anthropic 密钥      |   ⚡   | provider 为 `anthropic` 时必填   |
| `GOOGLE_API_KEY`            | Google Gemini 密钥  |   ⚡   | provider 为 `google` 时必填      |
| `ZHIPU_API_KEY`             | 智谱 AI 密钥        |   ⚡   | provider 为 `zhipu` 时必填       |
| `GROQ_API_KEY`              | Groq 密钥           |   ⚡   | provider 为 `groq` 时必填        |
| `QIANFAN_AK` / `QIANFAN_SK` | 百度千帆密钥对      |   ⚡   | provider 为 `qianfan` 时必填     |
| `SILICONFLOW_API_KEY`       | 硅基流动密钥        |   ⚡   | provider 为 `siliconflow` 时必填 |

⚡ = 使用对应 provider 时必填

---

## 相关文档

- [引擎配置](engine.md) — provider 和 model 详细说明
- [数据库配置](database.md) — 连接凭据配置
- [知识库配置](knowledge_base.md) — struct 目录映射规则
- [功能开关](features.md) — chat_history 和 file_upload 行为说明
- [模型支持](MODELS.md) — 全部支持的模型服务商
- [预设配置](preset_config.md) — 常见场景配置模板