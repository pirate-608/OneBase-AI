# Features 功能开关

`features` 字段用于控制前端界面和后端服务的可选功能。通过简单的布尔值即可启用或禁用特定能力，无需修改代码。

---

## 基本结构

```yaml title="onebase.yml"
features:
  chat_history: true
  file_upload: true
```

| 字段           | 类型 | 默认值 | 说明             |
| :------------- | :--- | :----: | :--------------- |
| `chat_history` | bool | `true` | 多轮对话历史记录 |
| `file_upload`  | bool | `true` | 前端实时文档上传 |

---

## chat_history — 对话历史

控制是否启用多轮对话记忆功能。

**启用时（`true`）：**

- 后端将每轮对话（用户提问 + AI 回答）持久化存储到 PostgreSQL
- 页面刷新后对话上下文不丢失
- 前端侧边栏显示"对话"标签页，可查看和切换历史会话

**禁用时（`false`）：**

- 后端不存储任何对话记录，每次提问都是独立的单轮问答
- 前端侧边栏隐藏"对话"标签页，仅显示知识库文件树
- 适用于隐私敏感场景或纯检索型应用

---

## file_upload — 文件上传

控制是否允许用户通过前端界面实时上传文档。

**启用时（`true`）：**

- 前端输入框旁显示文件上传按钮（📎）
- 支持上传 PDF / TXT / MD 文件
- 上传的文档即时切片入库，无需重新执行 `onebase build`
- 后端注册 `/upload` 路由处理文件

**禁用时（`false`）：**

- 前端隐藏上传按钮
- 后端 `/upload` 路由不注册，上传请求返回 403
- 知识库内容完全由 `onebase build` 管理，适用于只读知识库

---

## 配置流转

功能开关从配置文件到实际生效的完整链路：

```
onebase.yml → CLI 读取 → Docker 环境变量注入 → 后端条件路由 → 前端条件渲染
```

1. `onebase.yml` 中定义 `features.chat_history` / `features.file_upload`
2. `onebase build` / `onebase serve` 时将其注入为容器环境变量 `FEATURE_CHAT_HISTORY` / `FEATURE_FILE_UPLOAD`
3. 后端根据环境变量决定是否注册路由、是否存储对话
4. 前端通过 `/config` 接口获取开关状态，条件渲染 UI 组件

---

## 与性能参数的关系

`features` 负责“功能是否启用”，`performance` 负责“启用后如何控压和提速”。推荐组合如下：

- 开启 `features.chat_history` 时，建议同时开启 `performance.rate_limit_enabled`
- 开启 `features.file_upload` 时，建议设置较低的 `performance.upload_rate_limit_per_minute`
- 若有高频重复提问场景，建议开启 `performance.redis_cache_enabled` 并设置合适的 `redis_context_cache_ttl_seconds`

详见：[配置总览](overview.md) 中 `performance.*` 字段说明。

!!! tip
    修改 `features` 后需要重新执行 `onebase serve` 才能生效（无需重新 `build`）。
