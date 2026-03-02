# 目录结构

OneBase 项目的完整文件组织与各模块职责说明。

---

## 仓库全局结构

```
onebase-repo/
├── pyproject.toml          # 包元数据、依赖声明、入口点
├── MANIFEST.in             # sdist 打包时额外包含的文件
├── LICENSE                 # MIT 许可证
├── README.md               # 项目说明
├── mkdocs.yml              # 文档站点配置
├── onebase.yml             # 示例站点配置（开发用）
├── .env                    # 环境变量（不纳入版本控制）
│
├── onebase/                # 🐍 CLI 核心包
├── templates/              # 🐳 Docker 运行时模板
├── docs/                   # 📖 MkDocs 文档源文件
├── base/                   # 📚 示例知识库目录
└── overrides/              # 🎨 MkDocs 主题覆写
```

---

## onebase/ — CLI 核心包

CLI 工具的全部源码。通过 `pip install onebase-ai` 安装后，用户在命令行调用 `onebase` 命令。

```
onebase/
├── __init__.py         # 包初始化，版本号导出
├── cli.py              # Typer CLI 入口：init / build / serve / stop / get-deps
├── config.py           # Pydantic 数据模型（OneBaseConfig）
├── builder.py          # 知识库目录扫描与结构解析
├── chunker.py          # 文档切块（RecursiveCharacterTextSplitter）
├── indexer.py          # 向量入库（PGVector 写入）
├── factory.py          # 模型工厂（13 推理 + 10 嵌入 provider）
├── docker_runner.py    # Docker Compose 编排与生命周期管理
├── deps_manager.py     # 动态依赖检测（provider → PyPI 包映射）
├── db.py               # 数据库连接字符串单一来源
├── logger.py           # Rich 日志与 Console 全局实例
├── i18n.py             # 运行时国际化翻译函数 _()
├── locales/            # 语言包目录
│   └── zh.py           # 中文翻译表
└── requirements.txt    # 核心运行依赖清单
```

### 模块依赖关系

```
cli.py
 ├── config.py          ← 加载并校验 onebase.yml
 ├── builder.py         ← 扫描知识库目录
 ├── chunker.py         ← 文档切块
 ├── indexer.py         ← 向量入库
 │    ├── factory.py    ← 创建 Embedding 模型实例
 │    └── db.py         ← 构建数据库连接字符串
 ├── docker_runner.py   ← Docker Compose 编排
 │    └── db.py         ← 获取数据库凭据
 ├── deps_manager.py    ← 检测 provider 依赖
 ├── logger.py          ← 全局日志
 └── i18n.py            ← 翻译函数
```

### 关键文件说明

| 文件               | 职责                                                                                                                |
| :----------------- | :------------------------------------------------------------------------------------------------------------------ |
| `cli.py`           | Typer 应用主入口，注册 5 个子命令，处理全局选项（`--lang` / `--verbose` / `--quiet`）                               |
| `config.py`        | 6 个 Pydantic BaseModel 类，加载 `onebase.yml` 并做类型+约束校验                                                    |
| `factory.py`       | `ModelFactory` 静态类，按 provider 字符串动态 import 并实例化 LangChain 模型。包含 `_docker_rewrite()` 网络重写逻辑 |
| `docker_runner.py` | `DockerRunner` 类，生成 `docker-compose.yml`、拷贝模板、管理容器生命周期                                            |
| `db.py`            | `get_db_credentials()` 和 `build_db_url()`，消除数据库凭据散落在多处的问题                                          |
| `builder.py`       | `KnowledgeBuilder` 类，支持 `struct: default`（自动扫描）和手动字典两种模式                                         |
| `chunker.py`       | `DocumentProcessor` 类，基于 LangChain 的 `RecursiveCharacterTextSplitter` 切块，注入面包屑元数据                   |

---

## templates/ — Docker 运行时模板

`onebase build` / `onebase serve` 时，CLI 将此目录下的文件拷贝到 `.onebase/` 并构建 Docker 镜像。

```
templates/
├── backend/                # FastAPI 后端应用
│   ├── main.py             # FastAPI 应用入口，CORS、路由注册、SPA 托管
│   ├── config.py           # 环境变量读取（DATABASE_URL、provider、feature flags）
│   ├── database.py         # SQLAlchemy 模型（chat_messages、chat_session_meta）
│   ├── schemas.py          # Pydantic 请求/响应模型
│   ├── Dockerfile          # 后端容器构建文件
│   ├── requirements.txt    # 后端 Python 依赖（30 个包全版本锁定）
│   ├── routers/            # 路由模块
│   │   ├── chat.py         # /api/chat（SSE 流式）、/api/sessions、/api/history
│   │   ├── knowledge.py    # /api/tree、/api/file/{path}
│   │   └── upload.py       # /api/upload（文件上传 + 实时向量化）
│   └── engine/             # 预留的引擎扩展目录
│   └── vector_store/       # 预留的向量存储扩展目录
│
├── compose/                # Docker Compose 模板（预留）
│   └── docker-compose.base.yml
│
└── frontend/               # Vue 3 前端 SPA
    ├── index.html          # HTML 入口
    ├── package.json        # npm 依赖声明
    ├── vite.config.js      # Vite 构建配置
    ├── dist/               # 构建产物（随包分发）
    ├── public/             # 静态资源
    └── src/                # 源代码
        ├── App.vue         # 根组件（布局、初始化、Feature Flag 读取）
        ├── main.js         # Vue 应用挂载
        ├── style.css       # 全局样式 + Tailwind CSS 4 入口
        ├── assets/         # SVG Logo 等资源
        ├── components/     # UI 组件
        │   ├── Sidebar.vue     # 侧边栏（知识库树 + 会话列表双 Tab）
        │   ├── ChatArea.vue    # 对话区域（消息、输入、复制/下载按钮）
        │   ├── ChatList.vue    # 会话列表（新建、重命名、删除）
        │   ├── FilePreview.vue # 文档预览面板（MD 渲染 / PDF 文本提取）
        │   └── TreeNode.vue    # 递归目录树节点
        └── composables/    # 组合式函数
            └── useChat.js  # 聊天核心逻辑（SSE 解析、会话管理）
```

---

## 运行时生成目录

`onebase init` 和 `onebase build` 会在用户项目目录下生成以下结构：

```
my-ai-site/                 # 用户项目根目录
├── onebase.yml             # 站点配置
├── .env                    # 环境变量
├── requirements.txt        # 动态依赖
├── base/                   # 知识库文档
│   └── overview.md
└── .onebase/               # 运行时缓存（gitignore）
    ├── docker-compose.yml  # 生成的 Compose 文件
    └── backend/            # 后端构建上下文副本
        ├── main.py
        ├── factory.py      # 从 onebase 包拷贝
        ├── static/         # 前端 dist 拷贝
        └── ...
```

---

## 相关文档

- [后端实现](backend.md) — FastAPI 架构与路由设计
- [前端实现](frontend.md) — Vue 3 组件与组合式函数
- [API 文档](api.md) — 全部 HTTP 接口说明
