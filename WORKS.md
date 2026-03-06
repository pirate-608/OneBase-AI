# Here is the place to log agent works and plans.

---

## work-20260306 — P0–P4 阶段性审计与 P2 执行

### P0 — 关键缺陷（4/4 ✅ 全部完成）

| 编号 | 任务            | 状态  | 成果                                       |
| :--- | :-------------- | :---: | :----------------------------------------- |
| P0#1 | Pytest 测试框架 |   ✅   | 7 个测试文件、61+ 用例，CI 集成            |
| P0#2 | API Token 鉴权  |   ✅   | Bearer 中间件 + 白名单 + 前端 `useAuth.js` |
| P0#3 | Schema 输入加固 |   ✅   | Literal role、regex session_id、长度约束   |
| P0#4 | 模型/向量库单例 |   ✅   | `deps.py` 双重检查锁定，线程安全           |

### P1 — 核心功能增强（全部完成）

| 编号  | 任务                     | 状态  | 成果                                                          |
| :---- | :----------------------- | :---: | :------------------------------------------------------------ |
| P1#1  | Redis 缓存 + 速率限制    |   ✅   | FixedWindowRateLimiter，chat 30/min、upload 6/min，Redis 可选 |
| P1#2  | 上传同步向量化           |   ✅   | POST /api/upload 实时切块写入 PGVector                        |
| P1#3  | MkDocs 文档站 i18n       |   ✅   | 42 篇文档（21 中文 + 21 英文），i18n 插件                     |
| P1#4  | GitHub Pages 部署        |   ✅   | CI 自动构建并发布到 gh-pages 分支                             |
| P1#5  | Docker Model Runner      |   ✅   | 第 5 推理后端，desktop 模式免 GPU 配置                        |
| P1#6  | 自动模型拉取             |   ✅   | Ollama/Xinference/vLLM entrypoint 脚本自动 pull               |
| P1#7  | 配置管道 + Feature Flags |   ✅   | chat_history / file_upload 开关，前端动态读取                 |
| P1#8  | DOMPurify XSS 防护       |   ✅   | Markdown 渲染前 sanitize                                      |
| P1#9  | CORS 策略                |   ✅   | env 动态配置 CORS_ORIGINS，生产收紧                           |
| P1#10 | 路径遍历防护             |   ✅   | Path.resolve().is_relative_to() 校验                          |

### P2 — 生产就绪（3/3 ✅ 全部完成）

| 编号 | 任务                  | 状态  | 成果                                                                                                             |
| :--- | :-------------------- | :---: | :--------------------------------------------------------------------------------------------------------------- |
| P2#1 | Docker 生产加固       |   ✅   | db/backend healthcheck、backend 内存限制 2G、`pool_pre_ping=True`、`.env.example`、`depends_on: service_healthy` |
| P2#2 | 审计日志 + 结构化日志 |   ✅   | 请求 ID 中间件（`X-Request-ID`）、鉴权/上传/会话删除审计日志、`LOG_FORMAT=json` 选项                             |
| P2#3 | 路由集成测试          |   ✅   | `test_routers.py` 25 用例（health/tree/file/sessions/chat/upload/request-id/rate-limit），全部 86 测试通过       |

### P3 — 体验优化（待定）

| 编号 | 任务              | 状态  | 目标                               |
| :--- | :---------------- | :---: | :--------------------------------- |
| P3#1 | 前端错误提示      |   ⬚   | toast/modal 弹窗替代 console.error |
| P3#2 | 前端重试 + 加载态 |   ⬚   | 网络失败自动重试、骨架屏/spinner   |
| P3#3 | 会话/消息分页     |   ⬚   | 大量会话时分页加载，避免性能问题   |
| P3#4 | 文档补充          |   ⬚   | 故障排除、API 错误码参考、监控指南 |
| P3#5 | 数据库索引优化    |   ⬚   | created_at 索引、查询性能调优      |

### P4 — 远期规划

| 编号 | 任务               | 状态  | 目标                                    |
| :--- | :----------------- | :---: | :-------------------------------------- |
| P4#1 | 配置 schema 版本号 |   ⬚   | onebase.yml 增加 version 字段，兼容迁移 |
| P4#2 | Alembic 数据库迁移 |   ⬚   | 替代 create_all()，支持 schema 演进     |
| P4#3 | 数据保留策略       |   ⬚   | 聊天历史 TTL / 归档机制                 |
| P4#4 | 密钥轮换机制       |   ⬚   | API_TOKEN 过期 + 刷新流程               |
| P4#5 | 前端无障碍         |   ⬚   | ARIA 标签、键盘导航                     |
| P4#6 | 多用户支持         |   ⬚   | 用户隔离、权限模型                      |

---

**约定：每次对话结束后更新本文件，记录变更内容与状态流转。**

---

### 变更日志

#### 2026-03-06 — P2 生产就绪（3 项）

**P2#1 Docker 生产加固：**

- `onebase/docker_runner.py` — db 服务增加 `healthcheck`（`pg_isready`），backend 增加 `healthcheck`（Python urllib 探活 `/api/health`）
- `onebase/docker_runner.py` — backend `depends_on` 改为 `service_healthy` 条件，推理服务改为 `service_started`
- `onebase/docker_runner.py` — backend 增加 `deploy.resources.limits.memory: 2G`
- `templates/backend/database.py` — `create_engine` 增加 `pool_pre_ping=True` 消除连挂连接
- `.env.example` — 新建环境变量模板文件

**P2#2 审计日志 + 结构化日志：**

- `templates/backend/config.py` — 新增 `LOG_FORMAT` 环境变量（`text`/`json`）
- `templates/backend/main.py` — 新增请求 ID 中间件（`X-Request-ID` 头 + `ContextVar`），每请求记录 method/path/status/耗时
- `templates/backend/main.py` — 鉴权失败时记录 `logger.warning` 含 IP + 路径 + request_id
- `templates/backend/main.py` — `LOG_FORMAT=json` 时启用 JSON 格式 handler
- `templates/backend/routers/chat.py` — 新增 logger，会话删除时记录审计日志
- `templates/backend/routers/upload.py` — 上传成功/失败均记录审计日志（含文件名、chunks、字节数）

**P2#3 路由集成测试：**

- `tests/test_routers.py` — 新增 25 个集成测试用例：health(3)、tree(4)、file(3)、sessions(2)、history(2)、chat(3)、upload(4)、request-id(2)、rate-limit(2)
- 全部 86 测试通过（8 个测试文件）