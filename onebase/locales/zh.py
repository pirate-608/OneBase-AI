"""
Chinese (zh) translation table for OneBase CLI runtime output.

Keys are the English source strings used in _() calls.
Rich markup tags (e.g. [green], [bold cyan]) are preserved in translations.
"""

messages = {
    # ===== cli.py — init command =====
    "🚀 Welcome to [bold blue]OneBase[/bold blue]!": "🚀 欢迎使用 [bold blue]OneBase[/bold blue]!",
    "⚠️  {config} already exists. Use --force to overwrite.": "⚠️  {config} 已存在。使用 --force 覆盖。",
    "[green]✔[/green] Project initialized successfully!": "[green]✔[/green] 成功初始化项目！",
    "Next steps:\n"
    " 1. Edit [bold cyan]onebase.yml[/bold cyan] to configure your preferred model\n"
    " 2. Run [bold green]onebase get-deps > requirements.txt[/bold green] and install deps\n"
    " 3. Add documents and run [bold green]onebase build[/bold green] to build the knowledge base": "接下来你可以：\n"
    " 1. 修改 [bold cyan]onebase.yml[/bold cyan] 以配置你喜欢的模型\n"
    " 2. 运行 [bold green]onebase get-deps > requirements.txt[/bold green] 并安装依赖\n"
    " 3. 放入文档并运行 [bold green]onebase build[/bold green] 构建知识库",
    # --- init: generated file content ---
    "# Welcome to your Knowledge Base\n\nPlace your Markdown or PDF documents here.": "# 欢迎来到你的知识库\n\n在这里放置你的 Markdown 或 PDF 文档。",
    # .env comments
    "# ============ Database Config (auto-generated, feel free to change) ============": "# ============ 数据库配置 (自动生成，可自行修改) ============",
    "# ============ API Keys ============": "# ============ API Keys ============",
    "# OpenAI / DeepSeek API Key (leave empty if using local Ollama only)": "# OpenAI / DeepSeek API Key (如果完全使用本地 Ollama，此处可留空)",
    "# ModelScope SDK Token (for online model inference)": "# 魔搭社区 ModelScope SDK Token (在线调用大模型时使用)",
    "# ============ Security (optional) ============": "# ============ 安全配置 (可选) ============",
    "# Allowed CORS origins, comma-separated. Default * allows all": "# CORS 允许的前端域名，多个用逗号分隔，默认 * 允许所有",
    # requirements.txt content
    "# 📦 OneBase Dynamic Dependencies\n"
    "# After editing onebase.yml, run:\n"
    "# onebase get-deps > requirements.txt\n"
    "# Then:\n"
    "# pip install -r requirements.txt\n": "# 📦 OneBase 动态依赖文件\n"
    "# 请在修改完 onebase.yml 后，运行以下命令自动提取所需依赖：\n"
    "# onebase get-deps > requirements.txt\n"
    "# 然后执行：\n"
    "# pip install -r requirements.txt\n",
    # ===== cli.py — get-deps command =====
    "❌ {config} not found. Please run `onebase init` first.": "❌ 找不到 {config}。请先运行 `onebase init`。",
    "❌ Config parsing failed: {err}": "❌ 配置文件解析失败: {err}",
    # ===== cli.py — build command =====
    "❌ {config} not found. Run `onebase init` in your project root first.": "❌ 找不到 {config}。请先在项目根目录运行 `onebase init`。",
    "❌ Container conflict: only one local inference engine can be specified at a time.": "❌ 容器编排冲突：构建时只能同时指定一种本地推理容器引擎。",
    "📦 Reading config [bold cyan]{config}[/bold cyan]...": "📦 正在读取并校验配置 [bold cyan]{config}[/bold cyan]...",
    "❌ Invalid config, please check:\n{err}": "❌ 配置文件参数有误，请检查:\n{err}",
    "[green]✔[/green] Config loaded successfully!": "[green]✔[/green] 配置读取成功！",
    "\n[cyan]🔍 Scanning knowledge base directory...[/cyan]": "\n[cyan]🔍 正在扫描和解析知识库目录...[/cyan]",
    "⚠️  Knowledge base is empty — no valid MD/PDF/TXT files found.": "⚠️  知识库是空的，没有找到任何有效的 MD/PDF/TXT 文件。",
    "\n[cyan]✂️  Chunking documents (Chunk Size: {size})...[/cyan]": "\n[cyan]✂️  开始进行文档切片 (Chunk Size: {size})...[/cyan]",
    "Analyzing document structure and generating chunks...": "正在分析文档结构并生成切片...",
    "[green]✔[/green] Done! Generated [bold blue]{count}[/bold blue] memory chunks.": "[green]✔[/green] 完成！共生成 [bold blue]{count}[/bold blue] 个记忆片段。",
    "\n[cyan]💾 Starting backend services and writing data...[/cyan]": "\n[cyan]💾 准备启动后台基础服务并写入数据...[/cyan]",
    "Starting container group: {services}": "即将启动容器组: {services}",
    "💡 Note: If this is the first time using a containerized model, the embedding weights may not be downloaded yet. "
    "If ingestion fails, start containers with `serve` first to download the model, then run `build`.": "💡 注意：若这是首次启用容器化大模型，容器内可能尚未下载对应 Embedding 权重。"
    "若后续入库失败，请先使用 serve 命令启动容器并下载好模型后再进行 build。",
    "❌ Failed to start infrastructure. Make sure Docker is running. ({err})": "❌ 基础服务启动失败。请确保 Docker 已启动。({err})",
    "PG ready (attempt {n})": "PG 连接就绪 (第 {n} 次检测)",
    "⏳ PG not ready ({n}/{max}), retrying in 2s...": "⏳ PG 尚未就绪 ({n}/{max})，2s 后重试...",
    "❌ Database not ready within 30s. Check Docker container status.": "❌ 数据库在 30s 内未就绪，请检查 Docker 容器状态。",
    "[green]✔[/green] Successfully wrote [bold blue]{count}[/bold blue] vectors to the database!": "[green]✔[/green] 成功将 [bold blue]{count}[/bold blue] 个向量写入数据库！",
    "❌ Vector ingestion failed: {err}": "❌ 向量化写入失败: {err}",
    "💡 Hint: You may not have installed deps. Run `onebase get-deps > requirements.txt` then pip install.": "💡 提示: 可能是你尚未安装依赖，请运行 `onebase get-deps > requirements.txt` 并执行 pip install！",
    # ===== cli.py — serve command =====
    "❌ Config file not found. Run `onebase init` first.": "❌ 找不到配置文件。请先运行 `onebase init`。",
    "❌ Container conflict: only one local inference engine can be specified.": "❌ 容器编排冲突：你只能同时指定一种本地推理容器引擎。",
    "🐳 Parsing config and preparing Docker services...": "🐳 正在解析配置并准备启动 Docker 服务...",
    "Host Machine": "宿主机直连 (Host Machine)",
    "Bundled Ollama": "容器化集群 (Bundled Ollama)",
    "Bundled Xinference": "容器化集群 (Bundled Xinference)",
    "Bundled vLLM": "容器化集群 (Bundled vLLM)",
    "OneBase Status ({name})": "OneBase 运行状态 ({name})",
    "Component": "组件",
    "Configuration": "详细配置",
    "Reasoning Engine": "推理引擎 (Reasoning)",
    "Vector Store": "向量库 (Vector)",
    "Port": "服务端口 (Port)",
    "Compute Mode": "计算节点模式",
    "💡 First time? Make sure to download a model inside the container: "
    "`docker exec -it onebase_ollama ollama run <model>`": "💡 提示: 首次使用前请确保在容器内执行过 `docker exec -it onebase_ollama ollama run <模型名>` 下载模型。",
    "💡 After Xinference starts, visit `http://localhost:9997` to manage models.": "💡 提示: Xinference 启动后，请访问 `http://localhost:9997` 的 Web UI 管理模型。",
    "💡 vLLM is configured for the reasoning model in `onebase.yml`. "
    "Initial container startup may take a while to download weights.": "💡 提示: vLLM 已配置为启动 `onebase.yml` 中的推理模型，容器初始化可能需要较长时间下载权重。",
    "🚀 Orchestrating containers and starting API service...": "🚀 正在编排容器组并启动 API 服务...",
    "🎉 OneBase is running!\n\n"
    "🌐 URL: [bold underline cyan]http://localhost:{port}[/bold underline cyan]\n"
    "🛑 Stop: run [bold red]onebase stop[/bold red]": "🎉 OneBase 服务已启动！\n\n"
    "🌐 访问地址: [bold underline cyan]http://localhost:{port}[/bold underline cyan]\n"
    "🛑 停止服务: 运行 [bold red]onebase stop[/bold red]",
    "❌ Fatal error during startup: {err}": "❌ 启动过程中发生致命错误: {err}",
    # ===== cli.py — stop command =====
    "⚠️  No running service config found (.onebase/docker-compose.yml missing). Service may not be started.": "⚠️  找不到运行中的服务配置 (未发现 .onebase/docker-compose.yml)。可能服务尚未启动。",
    "🛑 Stopping OneBase containers...": "🛑 正在停止 OneBase 容器组...",
    "⚠️  Warning: Cleaning up data volumes — database and local model weights will be erased!": "⚠️  警告：正在清理数据卷，数据库与本地大模型权重都将被清空！",
    "Sending SIGTERM and removing networks...": "向容器发送 SIGTERM 信号并移除网络...",
    "[green]✔[/green] Services stopped and cleaned up!": "[green]✔[/green] 服务已成功停止并清理完毕！",
    "❌ Error stopping services: {err}": "❌ 停止服务时发生错误: {err}",
    # ===== docker_runner.py =====
    "⚠️  Frontend build artifacts (dist) not found. "
    "Run `npm run build` in templates/frontend first if you need the UI.": "⚠️  未找到前端构建产物(dist)。如果你需要 UI 界面，请先在 templates/frontend 执行 npm run build",
    "[dim]🌐 Pulling pre-built image {image} (timeout: 15s)...[/dim]": "[dim]🌐 尝试拉取预编译云端镜像 {image} (超时: 15s)...[/dim]",
    "[green]✅ Pre-built image pulled! Fast-start activated.[/green]": "[green]✅ 预编译镜像拉取成功！触发极速启动。[/green]",
    "[yellow]⚠️ Image not published or pull failed. Falling back to local build.[/yellow]": "[yellow]⚠️ 镜像未发布或拉取失败，智能回退至本地构建模式。[/yellow]",
    "[yellow]⚠️ Image pull timed out. Falling back to local build.[/yellow]": "[yellow]⚠️ 镜像拉取超时，智能回退至本地构建模式。[/yellow]",
    "[yellow]⚠️ Docker communication error ({err}). Falling back to local build.[/yellow]": "[yellow]⚠️ Docker 通信异常 ({err})，智能回退至本地构建模式。[/yellow]",
    "Docker Compose failed to start: {err}": "Docker Compose 启动失败: {err}",
}
