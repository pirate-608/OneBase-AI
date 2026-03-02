# 数据库设计

OneBase 使用 PostgreSQL + pgvector 扩展，同时承载向量检索和业务数据。

---

## 架构概览

```
PostgreSQL (pgvector/pgvector:pg16)
│
├── langchain_pg_collection    # PGVector 集合注册表
├── langchain_pg_embedding     # 向量数据表（文档切块 + 嵌入向量）
├── chat_messages              # 聊天消息历史
└── chat_session_meta          # 会话元数据
```

OneBase 中有两套表：

1. **PGVector 管理的表** — 由 LangChain PGVector 自动创建和维护，存储文档向量
2. **业务表** — 由 SQLAlchemy ORM 定义，存储聊天历史和会话信息

---

## 向量存储表

由 `langchain-postgres` 包的 `PGVector` 类自动管理，OneBase 不直接操作其 DDL。

### langchain_pg_collection

集合注册表，每个 OneBase 站点对应一条记录。

| 列          | 类型    | 说明                                                    |
| :---------- | :------ | :------------------------------------------------------ |
| `uuid`      | UUID    | 主键                                                    |
| `name`      | VARCHAR | 集合名称（由 `site_name` 生成：空格替换为 `_`，转小写） |
| `cmetadata` | JSONB   | 集合级元数据                                            |

### langchain_pg_embedding

文档切块的向量嵌入表，是 RAG 检索的核心数据源。

| 列              | 类型    | 说明                                       |
| :-------------- | :------ | :----------------------------------------- |
| `id`            | VARCHAR | 主键                                       |
| `collection_id` | UUID    | 外键 → `langchain_pg_collection.uuid`      |
| `embedding`     | VECTOR  | pgvector 向量列，维度由 Embedding 模型决定 |
| `document`      | TEXT    | 原始文本切块内容                           |
| `cmetadata`     | JSONB   | 切块元数据（见下方）                       |

**cmetadata 字段结构：**

```json
{
  "title": "overview",
  "breadcrumbs": "section1 > overview",
  "source_file": "overview.md"
}
```

- `title` — 文档标题（文件名去后缀）
- `breadcrumbs` — 面包屑导航路径（从 YAML struct 或自动扫描生成）
- `source_file` — 原始文件名

用户通过前端上传的文件，面包屑格式为 `User Upload > filename.pdf`。

---

## 业务表

由 `templates/backend/database.py` 中的 SQLAlchemy 声明式模型定义。

### chat_messages

聊天消息持久化表，每条用户提问和 AI 回复各存一行。

```python
class ChatMessageDB(Base):
    __tablename__ = "chat_messages"

    id         = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    role       = Column(String, nullable=False)    # 'user' | 'assistant'
    content    = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

| 列           | 类型        | 索引  | 说明                            |
| :----------- | :---------- | :---: | :------------------------------ |
| `id`         | INTEGER     |  PK   | 自增主键                        |
| `session_id` | VARCHAR     |   ✅   | 会话标识符（前端生成的随机 ID） |
| `role`       | VARCHAR     |   —   | `user` 或 `assistant`           |
| `content`    | TEXT        |   —   | 消息正文                        |
| `created_at` | TIMESTAMPTZ |   —   | 服务端自动写入时间戳            |

### chat_session_meta

会话元数据表，存储用户自定义的标题。

```python
class ChatSessionMeta(Base):
    __tablename__ = "chat_session_meta"

    session_id = Column(String, primary_key=True)
    title      = Column(String, nullable=True)
```

| 列           | 类型    | 说明                                                |
| :----------- | :------ | :-------------------------------------------------- |
| `session_id` | VARCHAR | 主键，与 `chat_messages.session_id` 关联            |
| `title`      | VARCHAR | 用户自定义标题（NULL 时前端取第一条消息前 15 字符） |

---

## 连接管理

### CLI 侧（onebase 包）

`onebase/db.py` 提供集中的连接字符串构建：

```python
# 凭据读取
get_db_credentials() → dict  # 从 .env 读取 POSTGRES_*

# 连接字符串
build_db_url()                          # CLI 连接宿主机
build_db_url(host_override="db")        # Docker 内部网络
```

连接格式：`postgresql+psycopg://user:pass@host:port/dbname`

### 后端侧（容器内）

`templates/backend/config.py` 直接从 `DATABASE_URL` 环境变量读取，由 `docker_runner.py` 注入。

`templates/backend/database.py` 实现懒初始化 + 重试连接：

```python
def _init_db(max_retries=10, retry_interval=2.0):
    # 循环尝试连接，应对 PG 容器启动时序
    for attempt in range(1, max_retries + 1):
        try:
            _engine = create_engine(DB_URL)
            with _engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            Base.metadata.create_all(bind=_engine)  # 自动建表
            return
        except Exception:
            time.sleep(retry_interval)
```

---

## 数据流

```
用户文档 (base/)
    ↓ builder.py — 扫描 & 解析
    ↓ chunker.py — 切块 + 元数据注入
    ↓ indexer.py — 调用 Embedding API
    ↓
langchain_pg_embedding (向量写入)
    ↓
相似度检索 ← /api/chat 请求
    ↓
chat_messages (对话持久化)
```

---

## Feature Flag 对数据库的影响

| Flag                  | 影响                                                                     |
| :-------------------- | :----------------------------------------------------------------------- |
| `chat_history: false` | `chat_messages` 和 `chat_session_meta` 表仍会被创建，但不写入数据        |
| `file_upload: false`  | 上传路由被禁用，`langchain_pg_embedding` 不会有 `User Upload` 来源的记录 |

---

## 数据清理

```bash
# 保留容器，清空向量数据（需重新 build）
docker exec -it <db_container> psql -U onebase -d onebase_db \
  -c "TRUNCATE langchain_pg_embedding, langchain_pg_collection CASCADE;"

# 保留容器，清空聊天历史
docker exec -it <db_container> psql -U onebase -d onebase_db \
  -c "TRUNCATE chat_messages, chat_session_meta;"

# 完全销毁（删除数据卷）
onebase stop -v
```

---

## 相关文档

- [数据库配置](../user-guide/config/database.md) — 凭据与环境变量
- [安全配置](../user-guide/config/security.md) — 密码生成与端口暴露
- [目录结构](project_structure.md) — 文件位置参考
