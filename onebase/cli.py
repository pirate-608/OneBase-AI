import os
import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print
from pydantic import ValidationError
from .config import OneBaseConfig
from .builder import KnowledgeBuilder
from .chunker import DocumentProcessor
from .docker_runner import DockerRunner
from .indexer import VectorStoreManager

# 初始化 Typer 应用和 Rich 控制台
app = typer.Typer(
    name="onebase",
    help="OneBase: 像配置静态网站一样，一键构建与部署 AI 动态服务",
    add_completion=False,
)
console = Console()

# 默认常量
CONFIG_FILE = "onebase.yml"
BASE_DIR = "base"
HIDDEN_DIR = ".onebase"

@app.command()
def init(
    force: bool = typer.Option(False, "--force", "-f", help="强制覆盖已存在的文件"),
):
    """
    初始化一个新的 OneBase 项目
    """
    console.print(Panel.fit("🚀 欢迎使用 [bold blue]OneBase[/bold blue]!", border_style="blue"))
    
    config_path = Path(CONFIG_FILE)
    base_path = Path(BASE_DIR)
    
    if config_path.exists() and not force:
        console.print(f"[yellow]⚠️  {CONFIG_FILE} 已存在。使用 --force 覆盖。[/yellow]")
        raise typer.Exit(code=1)

    # 1. 创建默认目录结构
    base_path.mkdir(exist_ok=True)
    (base_path / "overview.md").write_text("# 欢迎来到你的知识库\n\n在这里放置你的文档。", encoding="utf-8")
    Path(HIDDEN_DIR).mkdir(exist_ok=True)
    
    # 2. 生成默认的 onebase.yml
    default_yaml = """site_name: My AI Assistant
engine:
  reasoning:
    provider: ollama
    model: llama3:8b-instruct-q4_K_M
  embedding:
    provider: ollama
    model: nomic-embed-text:v1.5

database:
  type: postgresql
  vector_store: pgvector

knowledge_base:
  path: ./base
  chunk_size: 500
  # 留空或填写 default，系统会自动扫描 base 目录生成左侧导航树
  struct: default

features:
  - chat_history: true
  - file_upload: true
"""
    config_path.write_text(default_yaml, encoding="utf-8")
    
    # 3. 生成 .env 模板
    Path(".env").write_text("# Your API Key and BASE_URL here if needed\n# For example:\n# OPENAI_API_KEY=your_api_key_here\nONEBASE_BASE_URL=https://your_base_url_here\n", encoding="utf-8")

    console.print(f"[green]✔[/green] 成功初始化项目！")
    console.print(f"👉 下一步: 编辑 [bold cyan]{CONFIG_FILE}[/bold cyan] 和 [bold cyan].env[/bold cyan]，然后运行 [bold green]onebase build[/bold green]")


@app.command()
def build():
    """
    解析配置，处理文件切片，并构建向量知识库
    """
    if not Path(CONFIG_FILE).exists():
        console.print(f"[red]❌ 找不到 {CONFIG_FILE}。请先运行 `onebase init`。[/red]")
        raise typer.Exit(code=1)

    console.print(f"📦 正在读取并校验配置 [bold cyan]{CONFIG_FILE}[/bold cyan]...")
    
    try:
        config = OneBaseConfig.load(CONFIG_FILE)
    except ValidationError as e:
        console.print("\n[red]❌ 配置文件参数有误，请检查:[/red]")
        for err in e.errors():
            loc = " -> ".join([str(x) for x in err['loc']])
            console.print(f"  [yellow]➤ {loc}[/yellow]: {err['msg']}")
        raise typer.Exit(code=1)
    
    console.print(f"[green]✔[/green] 配置读取成功！")

    # --- 新增的 Builder 逻辑 ---
    console.print("\n[cyan]🔍 正在扫描和解析知识库目录...[/cyan]")
    
    builder = KnowledgeBuilder(
        base_path=config.knowledge_base.path, 
        struct=config.knowledge_base.struct
    )
    
    # 获取展平后的文档和缺失的文件
    valid_docs, missing_files = builder.parse()

    if missing_files:
        console.print("[red]❌ 在 base/ 目录中找不到以下文件:[/red]")
        for f in missing_files:
            console.print(f"  - [yellow]{f}[/yellow]")
        raise typer.Exit(code=1)
        
    if not valid_docs:
        console.print("[yellow]⚠️  知识库是空的，没有找到任何文件。[/yellow]")
        raise typer.Exit(code=1)

    console.print(f"[green]✔[/green] 成功解析知识库树，共找到 [bold blue]{len(valid_docs)}[/bold blue] 个源文件。")

    # --- 新增的 Chunking 逻辑 ---
    console.print(f"\n[cyan]✂️  开始读取文件并按 {config.knowledge_base.chunk_size} 字符切片...[/cyan]")
    
    # 初始化切片处理器
    processor = DocumentProcessor(chunk_size=config.knowledge_base.chunk_size)
    
    # 执行处理
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="读取并切割文档中...", total=None)
        chunks = processor.process(valid_docs)

    console.print(f"[green]✔[/green] 切片完成！共生成 [bold blue]{len(chunks)}[/bold blue] 个文本块。")

    # 打印前几个文本块供开发者预览
    console.print("\n[dim]👀 预览前 3 个文本块：[/dim]")
    for i, chunk in enumerate(chunks[:3]):
        console.print(f"\n[bold yellow]--- Chunk {i+1} ---[/bold yellow]")
        # 打印元数据（这是 RAG 的关键）
        console.print(f"[cyan]Metadata:[/cyan] {chunk.metadata}")
        
        # 限制打印长度，避免刷屏
        content = chunk.page_content
        display_text = content[:150] + "..." if len(content) > 150 else content
        console.print(f"[white]{display_text}[/white]")

    # ---------------------------

    console.print("\n[green]✔[/green] 构建流程（演示）完成！")
    # --- 新增的向量化与入库逻辑 ---
    console.print("\n[cyan]💾 准备将数据向量化并写入数据库...[/cyan]")

    # 1. 确保环境变量已加载 (读取本地 .env)
    if Path(".env").exists():
        from dotenv import load_dotenv
        load_dotenv(".env")

    # 2. 检查数据库状态，如果没启动，临时拉起
    runner = DockerRunner(config=config, port=8000)
    # 我们生成 compose 文件，并只启动 db 服务
    runner.build_compose_file()
    
    console.print("[dim]检查并确保 PostgreSQL (pgvector) 正在运行...[/dim]")
    import subprocess
    try:
        subprocess.run(
            ["docker", "compose", "-f", str(runner.compose_file), "up", "-d", "db"], 
            check=True, capture_output=True
        )
    except Exception as e:
        console.print("[red]❌ 数据库启动失败，请检查 Docker 状态。[/red]")
        raise typer.Exit(code=1)

    # 3. 执行入库
    try:
        indexer = VectorStoreManager(config)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(
                description=f"调用 {config.engine.embedding.provider} API 进行向量化并入库...", 
                total=None
            )
            
            # 关键步骤：执行 Embedding 并存入 PG
            total_inserted = indexer.ingest(chunks)
            
        console.print(f"[green]✔[/green] 成功将 [bold blue]{total_inserted}[/bold blue] 个向量写入 PostgreSQL 数据库！")

    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        error_msg_lower = error_msg.lower()

        # 场景 1：API Key 错误或未授权 (401)
        if "auth" in error_msg_lower or "api_key" in error_msg_lower or error_type == "AuthenticationError":
            console.print(Panel.fit(
                f"[bold red]❌ 身份验证失败 (Authentication Error)[/bold red]\n\n"
                f"当前模型商: [cyan]{config.engine.embedding.provider}[/cyan]\n"
                f"请检查你的 [bold].env[/bold] 文件，确认对应的 API Key 是否填写正确且有效。\n\n"
                f"[dim]底层反馈: {error_msg}[/dim]",
                border_style="red"
            ))
            
        # 场景 2：网络连接失败或本地 Ollama 未启动
        elif "connect" in error_msg_lower or "timeout" in error_msg_lower or error_type in ["APIConnectionError", "ConnectError"]:
            suggestion = "请检查你的网络连接，或确认是否需要配置代理。"
            if config.engine.embedding.provider == "ollama":
                suggestion = "由于你使用的是 Ollama，[bold yellow]请确认本地是否已经运行了 `ollama serve` 并且模型已下载。[/bold yellow]"
                
            console.print(Panel.fit(
                f"[bold red]❌ 网络连接失败 (Connection Error)[/bold red]\n\n"
                f"无法连接到 [cyan]{config.engine.embedding.provider}[/cyan] 的服务。\n"
                f"💡 {suggestion}\n\n"
                f"[dim]底层反馈: {error_type}[/dim]",
                border_style="red"
            ))
            
        # 场景 3：触发速率限制或余额不足 (429)
        elif "rate" in error_msg_lower or "429" in error_msg_lower or "insufficient_quota" in error_msg_lower:
            console.print(Panel.fit(
                f"[bold red]❌ 触及速率限制或余额不足 (Rate Limit / Quota)[/bold red]\n\n"
                f"你的请求速度过快，或者当前 API Key 的账户余额已耗尽。\n"
                f"💡 建议：登录 [cyan]{config.engine.embedding.provider}[/cyan] 控制台检查账单，或在配置中减小 `chunk_size`。\n\n"
                f"[dim]底层反馈: {error_msg}[/dim]",
                border_style="red"
            ))
            
        # 场景 4：其他未知错误
        else:
            console.print(Panel.fit(
                f"[bold red]❌ 发生未知内部错误[/bold red]\n\n"
                f"异常类型: {error_type}\n"
                f"异常详情: {error_msg}",
                border_style="red"
            ))
            
        raise typer.Exit(code=1)

    console.print("\n[green]🎉 构建流程全部完成！你的知识库已经具备了 AI 检索能力。[/green]")
    console.print("👉 下一步: 运行 [bold green]onebase serve[/bold green] 启动后端 API 与前端 UI")


@app.command()
def serve(
    port: int = typer.Option(8000, "--port", "-p", help="服务绑定的端口"),
    detach: bool = typer.Option(False, "--detach", "-d", help="后台运行"),
):
    """
    启动 OneBase 前后端服务 (基于 Docker)
    """
    if not Path(CONFIG_FILE).exists():
        console.print(f"[red]❌ 找不到 {CONFIG_FILE}。请先运行 `onebase init`。[/red]")
        raise typer.Exit(code=1)

    console.print("🐳 正在解析配置并准备启动 Docker 服务...")
    
    try:
        # 1. 加载配置
        config = OneBaseConfig.load(CONFIG_FILE)
        
        # 2. 打印启动概览表
        from rich.table import Table
        table = Table(title=f"OneBase 运行状态 ({config.site_name})")
        table.add_column("组件", style="cyan")
        table.add_column("详情", style="magenta")
        table.add_row("Reasoning Engine", f"{config.engine.reasoning.provider} ({config.engine.reasoning.model})")
        table.add_row("Vector DB", f"{config.database.vector_store}")
        table.add_row("Port", str(port))
        console.print(table)

        # 3. 初始化并启动 DockerRunner
        runner = DockerRunner(config=config, port=port)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="正在拉取镜像并启动容器 (这可能需要几分钟)...", total=None)
            
            # 执行 docker compose up
            runner.up(detach=True)

        console.print(Panel.fit(
            f"🎉 服务已成功启动！\n\n"
            f"🌐 API 访问地址: [bold underline cyan]http://localhost:{port}[/bold underline cyan]\n"
            f"🗄️  数据库端口: [bold]5432[/bold]\n\n"
            f"🛑 停止服务: 运行 [bold red]onebase stop[/bold red]",
            title="OneBase Server", border_style="green"
        ))

    except Exception as e:
        console.print(f"[red]❌ 启动失败: {e}[/red]")
        raise typer.Exit(code=1)
    
@app.command()
def stop(
    remove_volumes: bool = typer.Option(False, "--volumes", "-v", help="同时删除挂载的数据卷（警告：会清空数据库数据！）"),
):
    """
    优雅地停止并移除运行中的 OneBase 服务
    """
    import subprocess
    
    compose_file = Path(HIDDEN_DIR) / "docker-compose.yml"
    
    if not compose_file.exists():
        console.print("[yellow]⚠️  找不到运行中的服务配置 (未发现 .onebase/docker-compose.yml)。可能服务尚未启动。[/yellow]")
        raise typer.Exit(code=0)

    console.print("🛑 正在停止 OneBase 容器组...")
    
    cmd = ["docker", "compose", "-f", str(compose_file), "down"]
    
    # 如果用户带了 -v 参数，说明要彻底销毁数据
    if remove_volumes:
        console.print("[red]⚠️  警告：正在清理数据卷，数据库向量数据将被清空！[/red]")
        cmd.append("-v")
        
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="向容器发送 SIGTERM 信号并移除网络...", total=None)
            
            # 执行 docker compose down
            subprocess.run(cmd, check=True, capture_output=True, text=True)

        console.print("[green]✔[/green] 服务已成功停止并移除！")
        
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ 停止服务时发生错误:\n{e.stderr}[/red]")
        raise typer.Exit(code=1)
    except FileNotFoundError:
        console.print("[red]❌ 找不到 docker 命令，请检查 Docker 环境。[/red]")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()