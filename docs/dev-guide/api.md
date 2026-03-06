# API 文档

OneBase 后端基于 FastAPI，所有接口以 `/api` 为前缀。本页列出全部 HTTP 端点的请求/响应规范。

---

## 总览

| 方法   | 路径                         | 说明                     | Feature Flag   |
| :----- | :--------------------------- | :----------------------- | :------------- |
| GET    | `/api/health`                | 健康检查 + Feature Flags | —              |
| POST   | `/api/chat`                  | 流式对话（SSE）          | —              |
| GET    | `/api/sessions`              | 获取会话列表             | `chat_history` |
| PUT    | `/api/sessions/{session_id}` | 重命名会话               | `chat_history` |
| GET    | `/api/history/{session_id}`  | 获取指定会话历史         | `chat_history` |
| DELETE | `/api/history/{session_id}`  | 删除指定会话             | `chat_history` |
| GET    | `/api/tree`                  | 知识库目录树             | —              |
| GET    | `/api/file/{file_path}`      | 获取文档内容             | —              |
| POST   | `/api/upload`                | 上传文档并向量化         | `file_upload`  |

---

## 鉴权

当环境变量 `API_TOKEN` 非空时，除 `/api/health` 外的所有端点均需携带 Bearer Token：

```
Authorization: Bearer <API_TOKEN>
```

未携带或 Token 错误时返回：

```json
// 401 Unauthorized
{"detail": "Unauthorized"}
// 响应头: WWW-Authenticate: Bearer
```

`API_TOKEN` 未设置时所有请求放行。详见[安全配置](../user-guide/config/security.md#api-token-鉴权)。

---

## 健康检查

### GET /api/health

返回服务状态和 Feature Flags，供前端初始化时读取。

**响应 200：**

```json
{
  "status": "ok",
  "site_name": "My AI Assistant",
  "features": {
    "chat_history": true,
    "file_upload": true
  }
}
```

---

## 对话

### POST /api/chat

基于知识库的流式对话接口，使用 Server-Sent Events (SSE) 返回。

**请求体：**

```json
{
  "session_id": "session_abc123",
  "messages": [
    { "role": "user", "content": "什么是 OneBase？" }
  ],
  "stream": true
}
```

| 字段                 | 类型   | 必填  | 说明                                                                   |
| :------------------- | :----- | :---: | :--------------------------------------------------------------------- |
| `session_id`         | string |   —   | 会话 ID，默认 `"default-session"`，仅允许 `a-zA-Z0-9_-`，最长 128 字符 |
| `messages`           | array  |   ✅   | 消息列表（至少 1 条），最后一条为当前用户输入                          |
| `messages[].role`    | string |   ✅   | 仅允许 `"user"` 或 `"assistant"`                                       |
| `messages[].content` | string |   ✅   | 消息正文，1–50000 字符                                                 |
| `stream`             | bool   |   —   | 是否流式返回，默认 `true`                                              |

**响应**（`text/event-stream`）：

```
data: {"content": "OneBase 是"}

data: {"content": "一个 RAG 框架"}

data: [DONE]
```

每个 `data:` 行包含一个 JSON 对象，`content` 字段为增量文本。`[DONE]` 标记流结束。

**错误事件：**

```
data: {"error": "模型调用失败: Connection refused"}
```

**内部流程：**

1. 保存用户消息到 `chat_messages`（`chat_history` 开启时）
2. 拼接上下文锚点（上一条 AI 回复前 200 字符 + 当前问题）
3. 向量相似度检索（`similarity_search`，top 4 chunks）
4. 构建 System Prompt（注入检索结果 + 面包屑来源）
5. 流式调用 LLM（`llm.astream()`）
6. 流结束后保存 AI 回复到 `chat_messages`

---

## 会话管理

### GET /api/sessions

获取所有历史会话列表，按最后活跃时间降序排列。

**响应 200：**

```json
[
  {
    "id": "session_abc123",
    "title": "什么是 OneBase？...",
    "created_at": "2026-03-02T10:30:00+08:00"
  }
]
```

`title` 优先使用用户自定义标题（`chat_session_meta`），否则取第一条用户消息的前 15 个字符。

---

### PUT /api/sessions/{session_id}

重命名指定会话。

**请求体：**

```json
{
  "title": "关于 OneBase 的讨论"
}
```

| 字段    | 类型   | 说明               |
| :------ | :----- | :----------------- |
| `title` | string | 新标题，1–100 字符 |

**响应 200：**

```json
{
  "status": "success",
  "title": "关于 OneBase 的讨论"
}
```

---

### GET /api/history/{session_id}

获取指定会话的完整消息历史，按时间升序排列。

**响应 200：**

```json
[
  { "role": "user", "content": "什么是 OneBase？" },
  { "role": "assistant", "content": "OneBase 是一个..." }
]
```

---

### DELETE /api/history/{session_id}

删除指定会话的所有消息记录。

**响应 200：**

```json
{ "status": "success" }
```

---

## 知识库

### GET /api/tree

获取知识库目录树结构。根据 `onebase.yml` 中的 `struct` 配置：

- `struct: default` → 自动扫描 `base/` 目录
- `struct: {dict}` → 按手动配置的字典结构返回

**响应 200：**

```json
[
  {
    "title": "section1",
    "type": "folder",
    "isOpen": false,
    "children": [
      { "title": "overview", "type": "file", "path": "section1/overview.md" }
    ]
  },
  { "title": "faq", "type": "file", "path": "faq.txt" }
]
```

| 字段       | 类型   | 说明                                |
| :--------- | :----- | :---------------------------------- |
| `title`    | string | 显示标题                            |
| `type`     | string | `"folder"` 或 `"file"`              |
| `isOpen`   | bool   | 文件夹默认折叠状态                  |
| `children` | array  | 子节点（仅文件夹）                  |
| `path`     | string | 相对于 `base/` 的文件路径（仅文件） |

---

### GET /api/file/{file_path}

获取指定文档的文本内容。支持 Markdown、TXT 和 PDF（文本提取）。

**路径参数：** `file_path` — 相对于 `base/` 的文件路径

**响应 200：**

```json
{ "content": "# Welcome\n\nThis is the overview document..." }
```

**PDF 响应格式：**

```json
{ "content": "**--- 第 1 页 ---**\n\n页面内容...\n\n**--- 第 2 页 ---**\n\n..." }
```

**错误 403：**

```json
{ "detail": "禁止跨目录访问" }
```

路径遍历防护：后端使用 `Path.resolve().is_relative_to()` 检查真实路径是否在 `base/` 内。

---

## 文件上传

### POST /api/upload

上传文档并实时向量化写入知识库。仅在 `file_upload: true` 时可用。

**请求：** `multipart/form-data`

| 字段   | 类型 | 说明                         |
| :----- | :--- | :--------------------------- |
| `file` | File | 上传的文件（PDF / TXT / MD） |

**限制：**

- 文件大小上限：20 MB
- 支持格式：`.pdf`、`.txt`、`.md`

**响应 200：**

```json
{
  "status": "success",
  "filename": "api-reference.pdf",
  "chunks": 42
}
```

**错误响应：**

| 状态码 | 说明                               |
| :----- | :--------------------------------- |
| 400    | 不支持的文件格式                   |
| 403    | 文件上传功能已关闭（Feature Flag） |
| 413    | 文件大小超过 20 MB 限制            |
| 500    | 服务器处理失败（日志中记录详情）   |

**内部流程：**

1. 校验文件格式和大小
2. 写入临时文件 → 加载并解析
3. `RecursiveCharacterTextSplitter` 切块（chunk_size=500, overlap=50）
4. 注入元数据 `breadcrumbs: "User Upload > filename"`
5. 调用 Embedding 模型向量化
6. 写入 pgvector

---

## 静态资源

### GET /{catchall}

SPA 前端托管。后端将 Vue 构建产物挂载为静态文件：

- `/assets/*` — 带 Hash 的构建产物，开启强缓存（`max-age=31536000, immutable`）
- 其余路径 — 回退到 `index.html`，设置 `no-cache` 确保用户始终获取最新入口

---

## 相关文档

- [后端实现](backend.md) — 路由模块与中间件设计
- [前端实现](frontend.md) — 前端如何调用这些接口
- [数据库设计](database_design.md) — 表结构与数据流
