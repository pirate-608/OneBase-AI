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

| 编号 | 任务                     | 状态  | 目标                                            | 难度  | 收益  |
| :--- | :----------------------- | :---: | :---------------------------------------------- | :---: | :---: |
| P3#1 | 前端错误提示             |   ⬚   | toast/modal 弹窗替代 console.error              |  低   |  中   |
| P3#2 | 前端重试 + 加载态        |   ⬚   | 网络失败自动重试、骨架屏/spinner                |  低   |  中   |
| P3#3 | 会话/消息分页            |   ⬚   | 大量会话时分页加载，避免性能问题                |  中   |  中   |
| P3#4 | 文档补充                 |   ⬚   | 故障排除、API 错误码参考、监控指南              |  低   |  高   |
| P3#5 | 数据库索引优化           |   ⬚   | created_at 索引、查询性能调优                   |  低   |  中   |
| P3#6 | CPU 密集型操作线程池隔离 |   ⬚   | chunker/indexer 使用 ProcessPoolExecutor        |  中   |  中   |
| P3#7 | 健康检查监控增强         |   ⬚   | /api/health 超时告警、独立探针、Prometheus 指标 |  低   |  中   |

**P3#6 说明**：当前已用 `run_in_threadpool` 隔离 I/O 密集型（DB、embedding API），但 `chunker.py` 的大文档切块、`indexer.py` 的向量化是 CPU 密集型，应改用 `ProcessPoolExecutor` 绕过 GIL，提升 `build` 命令性能。

**P3#7 说明**：健康检查是"煤矿金丝雀"，应加超时监控（如 5s still pending = 事件循环异常）。可集成 Prometheus `/metrics` 端点暴露响应时间分布。

### P4 — 远期规划

| 编号 | 任务               | 状态  | 目标                                           | 难度  | 收益  |
| :--- | :----------------- | :---: | :--------------------------------------------- | :---: | :---: |
| P4#1 | 配置 schema 版本号 |   ⬚   | onebase.yml 增加 version 字段，兼容迁移        |  低   |  中   |
| P4#2 | Alembic 数据库迁移 |   ⬚   | 替代 create_all()，支持 schema 演进            |  中   |  高   |
| P4#3 | 数据保留策略       |   ⬚   | 聊天历史 TTL / 归档机制                        |  中   |  中   |
| P4#4 | 密钥轮换机制       |   ⬚   | API_TOKEN 过期 + 刷新流程                      |  中   |  中   |
| P4#5 | 前端无障碍         |   ⬚   | ARIA 标签、键盘导航                            |  低   |  中   |
| P4#6 | 多用户支持         |   ⬚   | 用户隔离、权限模型                             |  高   |  高   |
| P4#7 | 全异步架构改造     |   ⬚   | SQLAlchemy async + asyncpg / httpx AsyncClient |  高   |  高   |

**P4#7 说明**：彻底拥抱异步生态，消除 `run_in_threadpool` workaround。需改造：
- `database.py` — `AsyncSession`, `create_async_engine`
- `deps.py` — 单例改为 async 初始化
- 所有路由 — `await db.commit()`, `await vector_store.asimilarity_search()`
- 向量存储 — 检查 LangChain 是否支持 PGVector 异步，或自建 asyncpg 客户端
- HTTP 客户端 — Ollama/Xinference SDK 检查是否有 httpx 后端

**风险**：Breaking Change，需全面回归测试。LangChain 异步支持不完整，部分功能可能需自建适配层。建议在分支中完整验证后再合并主线。

---

**约定：每次对话结束后更新本文件，记录变更内容与状态流转。**

---

### 变更日志

#### 2026-03-07 — CI 依赖修复 + Docker 卷隔离 + 事件循环阻塞修复

**CI 依赖修复：**

- `pyproject.toml` — test deps 添加 `langchain-community`, `langchain-text-splitters`（chunker.py 顶层导入）
- `tests/test_builder.py` — 改用 `tmp_path` 替代 gitignored `base/` 目录
- `pyproject.toml` + `templates/backend/requirements.txt` — 修复 `requests` 版本冲突（>=2.32.5）
- `templates/backend/requirements.txt` — 删除 `langchain-modelscope-integration`（与 langchain-core 1.x 冲突）
- `templates/backend/requirements.txt` — 全部依赖精确锁定 `==` 版本，消除 pip 回溯爆炸
- `onebase/cli.py` — 修复 `\ud83d\udce6` surrogate pair → `\U0001F4E6`
- `pyproject.toml` + `templates/backend/requirements.txt` — 版本 bump 到 0.1.4，langchain 生态升级到 1.x
- `pyproject.toml` — `langchain-community`, `langchain-text-splitters` 移入核心依赖（chunker.py 导入）

**Docker 卷隔离：**

- `onebase/docker_runner.py` — 卷名从硬编码 `pgdata` 改为项目隔离 `{site_name}_pgdata`（同样应用到 `ollama_data`, `xinference_data`, `vllm_data`），防止多项目密码冲突

**服务启动修复：**

- `onebase/docker_runner.py` — `up()` 始终传 `-d`（容器 detach），避免阻塞
- `onebase/cli.py` — Status panel 从 `if detach:` 分支移到无条件输出，非 detach 模式追加查看日志提示

**事件循环阻塞修复（关键）：**

- `templates/backend/routers/chat.py` — `async def chat_endpoint` 中同步调用 `db.commit()` 和 `vector_store.similarity_search()` 导致 uvicorn 单事件循环冻结，表现为 8000 端口完全不响应
- 修复：用 `run_in_threadpool()` 包裹同步调用，移入工作线程执行
- `templates/backend/Dockerfile` — uvicorn 改为 `--workers 2` 增加并发容错
- 新增 P3#6（CPU 密集型线程池）、P3#7（健康检查监控）、P4#7（全异步架构改造）到 WORKS.md

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