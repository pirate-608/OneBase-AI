# 安全配置

OneBase 涉及 API 密钥、数据库凭据和网络访问控制。本页说明各安全机制及推荐做法。

---

## .env 文件与密钥管理

`onebase init` 会自动生成 `.env` 文件，其中包含随机数据库密码：

```bash title=".env（自动生成）"
POSTGRES_USER=onebase
POSTGRES_PASSWORD=<随机 22 字符 URL-safe token>   # secrets.token_urlsafe(16)
POSTGRES_DB=onebase_db
```

### 最佳实践

| 做法                 | 说明                                                         |
| :------------------- | :----------------------------------------------------------- |
| **不要提交 `.env`**  | 项目已在 `.gitignore` 中排除，请确认 `.env` 不会进入版本控制 |
| **每个环境独立密码** | 开发、生产环境使用不同的 `POSTGRES_PASSWORD`                 |
| **最小化密钥范围**   | 只填写实际使用的 provider 密钥，其余留空                     |
| **定期轮换密钥**     | 对云服务 API Key 定期更换，更换后重启服务即可                |

### API 密钥存放

所有 API 密钥均通过 `.env` 注入，**不应写入 `onebase.yml`**：

```bash title=".env"
# 按需填写，只填对应 provider
OPENAI_API_KEY=sk-...
DASHSCOPE_API_KEY=sk-...
DEEPSEEK_API_KEY=sk-...
```

密钥在运行时通过环境变量传递给 Docker 容器（`env_file` 方式），不会出现在 Docker 镜像或 Compose 文件中。

---

## CORS 跨域策略

后端通过 `CORS_ORIGINS` 环境变量控制允许的前端来源。

### 默认行为

```python
# templates/backend/main.py
_cors_origins_raw = os.getenv("CORS_ORIGINS", "*")
```

| 场景     | `CORS_ORIGINS` 值             | 效果                         |
| :------- | :---------------------------- | :--------------------------- |
| 本地开发 | 缺省（`*`）                   | 允许所有来源，不携带凭据     |
| 生产部署 | `https://yourdomain.com`      | 仅允许指定域名，开启凭据传递 |
| 多域名   | `https://a.com,https://b.com` | 逗号分隔，每个域名独立匹配   |

### 配置方法

在 `.env` 中设置：

```bash title=".env"
# 生产环境：限制为实际前端域名
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

!!! warning "生产环境务必收紧"
    默认 `*` 仅适用于本地开发。部署到公网后，**必须**设置 `CORS_ORIGINS` 为实际域名，否则任意网站可调用你的 API。

### 凭据传递逻辑

```python
allow_credentials=(_cors_origins != ["*"])
```

- `CORS_ORIGINS=*` → `allow_credentials=False`（浏览器不发送 Cookie）
- 指定域名 → `allow_credentials=True`（允许 Cookie / Authorization 头）

---

## 数据库安全

### 密码生成

`onebase init` 使用 Python `secrets` 模块生成密码：

```python
import secrets
db_password = secrets.token_urlsafe(16)  # 22 字符，加密安全随机
```

生成的密码满足：

- 128 位熵（`token_urlsafe(16)` = 16 字节 = 128 bit）
- URL-safe 字符集（`A-Z a-z 0-9 - _`）
- 无硬编码后备值 — 如果 `POSTGRES_PASSWORD` 未设置，连接将因空密码失败

### 端口暴露

Docker Compose 中数据库端口映射到宿主机：

```yaml
services:
  db:
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
```

| 环境       | 建议                                          |
| :--------- | :-------------------------------------------- |
| 本地开发   | 默认 `5432` 映射即可                          |
| 生产服务器 | 移除 `ports` 映射，仅通过 Docker 内部网络访问 |
| 云服务器   | 防火墙规则阻止外部访问 5432                   |

---

## Docker 网络隔离

### 内部通信

OneBase 的 Docker Compose 架构中，各服务通过内部网络通信：

```
┌─────────────────────────────────────────┐
│          Docker 内部网络                 │
│                                         │
│  backend ──(db:5432)──▶ db (PostgreSQL) │
│  backend ──(ollama:11434)──▶ ollama     │
│                                         │
└─────────────────────────────────────────┘
        │                          
   ports: 8000                     
        ▼                          
    宿主机 / 外部访问               
```

- **后端 → 数据库**：通过服务名 `db` 访问，不经过宿主机网络
- **后端 → Ollama**：通过服务名 `ollama` 或 `host.docker.internal` 访问
- **外部只暴露**：后端 API 端口（默认 8000）

### host.docker.internal 重写

当容器内访问宿主机服务时，OneBase 自动将 `localhost` 重写为 `host.docker.internal`：

```python
# onebase/factory.py
def _docker_rewrite(url: str) -> str:
    if os.getenv("RUNNING_IN_DOCKER") == "true":
        return url.replace("localhost", "host.docker.internal")
    return url
```

此机制确保容器内能正确访问宿主机上的 Ollama 等服务，同时`docker-compose.yml`中 `extra_hosts` 配置保证 DNS 解析：

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

---

## 生产部署安全清单

部署到公网前，请逐项检查：

- [ ] `.env` 已从版本控制中排除
- [ ] `POSTGRES_PASSWORD` 使用强随机密码
- [ ] `CORS_ORIGINS` 设置为实际前端域名（非 `*`）
- [ ] 数据库端口未暴露到公网（移除 `ports` 或配置防火墙）
- [ ] API 密钥使用最小权限策略
- [ ] 后端端口通过反向代理（Nginx / Caddy）提供 HTTPS
- [ ] Docker 镜像使用固定版本标签，非 `latest`

---

## 相关文档

- [数据库配置](database.md) — 凭据字段详细说明
- [引擎配置](engine.md) — API 密钥与 provider 对应关系
- [字段参考](overview.md#环境变量速查表env) — 环境变量速查表
