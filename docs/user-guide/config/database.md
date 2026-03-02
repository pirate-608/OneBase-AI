# Database 数据库配置

`database` 字段定义 OneBase 使用的数据库类型和向量存储引擎。

---

## 基本结构

```yaml title="onebase.yml"
database:
  type: postgresql
  vector_store: pgvector
```

| 字段           | 类型   | 唯一合法值   | 说明             |
| :------------- | :----- | :----------- | :--------------- |
| `type`         | string | `postgresql` | 关系型数据库类型 |
| `vector_store` | string | `pgvector`   | 向量存储引擎     |

!!! warning "当前版本不支持扩展"
    OneBase 目前仅支持 **PostgreSQL + pgvector** 组合。填写其他值（如 `mysql`、`milvus`）将在配置加载阶段直接报错退出。未来版本可能会扩展对更多数据库和向量引擎的支持。

---

## 连接凭据

数据库连接信息通过 `.env` 环境变量配置，**不在 `onebase.yml` 中填写**：

```bash title=".env"
POSTGRES_USER=onebase              # 用户名
POSTGRES_PASSWORD=xxxxxxxx         # 密码（onebase init 自动生成）
POSTGRES_DB=onebase_db             # 数据库名
POSTGRES_HOST=localhost            # 可选，默认 localhost
POSTGRES_PORT=5432                 # 可选，默认 5432
```

`onebase init` 会自动生成安全的随机密码写入 `.env`，通常无需手动修改。
