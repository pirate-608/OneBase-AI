import os
import sys
import typer
from pathlib import Path
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from pydantic import ValidationError

# 相对导入包内模块
from .config import OneBaseConfig
from .builder import KnowledgeBuilder
from .chunker import DocumentProcessor
from .docker_runner import DockerRunner
from .indexer import VectorStoreManager
from .deps_manager import get_required_packages

# 🌟 引入独立解耦的日志与 UI 中枢
from .logger import logger, console, err_console, setup_logger

# 🌟 运行时 i18n 翻译函数
from .i18n import _, set_lang

app = typer.Typer(
    name="onebase",
    help="OneBase: Build & deploy AI services like configuring a static site",
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)

# 默认常量
CONFIG_FILE = "onebase.yml"
BASE_DIR = "base"
HIDDEN_DIR = ".onebase"


def version_callback(value: bool):
    """Handle the global -V flag."""
    if value:
        # 🌟 [1-1] 与 __init__.py 统一，从 pyproject.toml 元数据获取版本号
        try:
            from importlib.metadata import version

            ver = version("onebase-ai")
        except Exception:
            ver = "dev"
        print(f"OneBase CLI, version {ver}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-V",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
    lang: str = typer.Option(
        "en",
        "--lang",
        "-l",
        help="Output language: en, zh",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output (debug mode)"
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Quiet mode (errors only, for CI)"
    ),
):
    """
    OneBase - Build & deploy AI services like configuring a static site.
    """
    # 🌟 设置语言（必须在 setup_logger 之前，以便首条日志即可翻译）
    set_lang(lang)

    if quiet:
        setup_logger("ERROR")
    elif verbose:
        setup_logger("DEBUG")
    else:
        setup_logger("INFO")


@app.command()
def init(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
):
    """
    Initialize a new OneBase project with base directory and config files.
    """
    console.print(
        Panel.fit(
            _("🚀 Welcome to [bold blue]OneBase[/bold blue]!"), border_style="blue"
        )
    )

    config_path = Path(CONFIG_FILE)
    base_path = Path(BASE_DIR)

    if config_path.exists() and not force:
        logger.warning(
            _("⚠️  {config} already exists. Use --force to overwrite.").format(
                config=CONFIG_FILE
            )
        )
        raise typer.Exit(code=1)

    # Create base directory structure
    base_path.mkdir(exist_ok=True)
    (base_path / "overview.md").write_text(
        _(
            "# Welcome to your Knowledge Base\n\nPlace your Markdown or PDF documents here."
        ),
        encoding="utf-8",
    )

    # 创建运行缓存目录
    Path(HIDDEN_DIR).mkdir(exist_ok=True)

    # 写入默认配置模板
    default_yaml = """site_name: My AI Assistant
engine:
  reasoning:
    provider: ollama
    model: deepseek-r1:1.5b
  embedding:
    provider: ollama
    model: nomic-embed-text:v1.5
database:
  type: postgresql
  vector_store: pgvector
knowledge_base:
  path: ./base
  chunk_size: 500
  struct: default
features:
  chat_history: true
  file_upload: true
performance:
    redis_cache_enabled: true
    redis_context_cache_ttl_seconds: 300
    rate_limit_enabled: true
    chat_rate_limit_per_minute: 30
    upload_rate_limit_per_minute: 6
"""
    config_path.write_text(default_yaml, encoding="utf-8")

    # 🌟 [3-1] 初始化环境变量模板，自动生成随机数据库密码
    import secrets

    db_password = secrets.token_urlsafe(16)

    env_content = f"""{_("# ============ Database Config (auto-generated, feel free to change) ============")}
POSTGRES_USER=onebase
POSTGRES_PASSWORD={db_password}
POSTGRES_DB=onebase_db

{_("# ============ API Keys ============")}
{_("# OpenAI / DeepSeek API Key (leave empty if using local Ollama only)")}
{_("# For example: OPENAI_API_KEY=sk-xxxxxx)")}

{_("# ============ Security (optional) ============")}
{_("# Allowed CORS origins, comma-separated. Default * allows all")}
# CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

{_("# ============ Redis (optional, for cache/rate-limit) ============")}
{_("# Keep empty to disable Redis and fallback to in-memory strategy")}
# REDIS_URL=redis://redis:6379/0
"""
    Path(".env").write_text(env_content, encoding="utf-8")

    # Write bootstrap requirements.txt
    req_content = (
        "# \U0001f4e6 OneBase Dynamic Dependencies\n"
        "# After editing onebase.yml, run:\n"
        "# onebase get-deps > requirements.txt\n"
        "# Then:\n"
        "# pip install -r requirements.txt\n"
    )
    Path("requirements.txt").write_text(req_content, encoding="utf-8")

    logger.info(_("[green]\u2714[/green] Project initialized successfully!"))
    logger.info(
        _(
            "Next steps:\n"
            " 1. Edit [bold cyan]onebase.yml[/bold cyan] to configure your preferred model\n"
            " 2. Run [bold green]onebase get-deps > requirements.txt[/bold green] and install deps\n"
            " 3. Add documents and run [bold green]onebase build[/bold green] to build the knowledge base"
        )
    )


@app.command(name="get-deps")
def get_deps():
    """
    Detect required PyPI packages from onebase.yml (supports > redirect).
    """
    if not Path(CONFIG_FILE).exists():
        err_console.print(
            "[red]"
            + _("❌ {config} not found. Please run `onebase init` first.").format(
                config=CONFIG_FILE
            )
            + "[/red]"
        )
        raise typer.Exit(code=1)

    try:
        config = OneBaseConfig.load(CONFIG_FILE)
        packages = get_required_packages(config)

        for pkg in packages:
            sys.stdout.write(f"{pkg}\n")

    except Exception as e:
        err_console.print(
            "[red]" + _("❌ Config parsing failed: {err}").format(err=e) + "[/red]"
        )
        raise typer.Exit(code=1)


@app.command()
def build(
    with_ollama: bool = typer.Option(
        False, "--with-ollama", help="Start Ollama container for local embedding"
    ),
    with_xinference: bool = typer.Option(
        False, "--with-xinference", help="Start Xinference container"
    ),
    with_vllm: bool = typer.Option(False, "--with-vllm", help="Start vLLM container"),
    with_docker_model: bool = typer.Option(
        False,
        "--with-docker-model",
        help="Use Docker Model Runner (Docker Desktop 4.40+)",
    ),
    use_gpu: bool = typer.Option(
        False,
        "--use-gpu",
        "-g",
        help="Enable NVIDIA GPU passthrough for inference containers",
    ),
):
    """
    Parse config, chunk documents, and build the vector knowledge base.
    """
    if not Path(CONFIG_FILE).exists():
        logger.error(
            _(
                "❌ {config} not found. Run `onebase init` in your project root first."
            ).format(config=CONFIG_FILE)
        )
        raise typer.Exit(code=1)

    flags = sum([with_ollama, with_xinference, with_vllm])
    if flags > 1:
        logger.error(
            _(
                "❌ Container conflict: only one local inference engine can be specified at a time."
            )
        )
        raise typer.Exit(code=1)

    logger.info(
        _("📦 Reading config [bold cyan]{config}[/bold cyan]...").format(
            config=CONFIG_FILE
        )
    )
    try:
        config = OneBaseConfig.load(CONFIG_FILE)
    except ValidationError as e:
        logger.error(_("❌ Invalid config, please check:\n{err}").format(err=e))
        raise typer.Exit(code=1)

    logger.info(_("[green]✔[/green] Config loaded successfully!"))
    logger.info(_("\n[cyan]🔍 Scanning knowledge base directory...[/cyan]"))

    builder = KnowledgeBuilder(
        base_path=config.knowledge_base.path, struct=config.knowledge_base.struct
    )
    valid_docs, missing_files = builder.parse()

    if not valid_docs:
        logger.warning(
            _("⚠️  Knowledge base is empty — no valid MD/PDF/TXT files found.")
        )
        raise typer.Exit(code=1)

    logger.info(
        _("\n[cyan]✂️  Chunking documents (Chunk Size: {size})...[/cyan]").format(
            size=config.knowledge_base.chunk_size
        )
    )
    processor = DocumentProcessor(chunk_size=config.knowledge_base.chunk_size)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console,
    ) as progress:
        progress.add_task(
            description=_("Analyzing document structure and generating chunks..."),
            total=None,
        )
        chunks = processor.process(valid_docs)

    logger.info(
        _(
            "[green]✔[/green] Done! Generated [bold blue]{count}[/bold blue] memory chunks."
        ).format(count=len(chunks))
    )
    logger.info(_("\n[cyan]💾 Starting backend services and writing data...[/cyan]"))

    runner = DockerRunner(
        config=config,
        port=8000,
        with_ollama=with_ollama,
        with_xinference=with_xinference,
        with_vllm=with_vllm,
        with_docker_model=with_docker_model,
        use_gpu=use_gpu,
    )
    runner.build_compose_file()

    # 动态决定要拉起的容器组 (docker-model 使用 provider 类型，Docker 自动管理)
    services_to_start = ["db"]
    if with_ollama:
        services_to_start.append("ollama")
    if with_xinference:
        services_to_start.append("xinference")
    if with_vllm:
        services_to_start.append("vllm")

    import subprocess

    try:
        logger.debug(
            _("Starting container group: {services}").format(
                services=", ".join(services_to_start)
            )
        )

        if flags > 0:
            logger.warning(
                _(
                    "💡 Note: If this is the first time using a containerized model, models will be auto-pulled but the download may take a while. "
                    "If ingestion fails, wait for the model download to finish and try again."
                )
            )

        subprocess.run(
            ["docker", "compose", "-f", str(runner.compose_file), "up", "-d"]
            + services_to_start,
            check=True,
            capture_output=True,
        )
    except Exception as e:
        logger.error(
            _(
                "❌ Failed to start infrastructure. Make sure Docker is running. ({err})"
            ).format(err=e)
        )
        raise typer.Exit(code=1)

    # 🌟 [2-1] 等待 PG 容器真正就绪后再入库，避免启动时序导致的连接失败
    import time
    from sqlalchemy import create_engine, text as sa_text
    from .db import build_db_url

    _wait_conn = build_db_url()
    _max_wait = 15  # 最多等待 15 次 × 2s = 30s
    for _attempt in range(1, _max_wait + 1):
        try:
            _tmp_engine = create_engine(_wait_conn)
            with _tmp_engine.connect() as _conn:
                _conn.execute(sa_text("SELECT 1"))
            _tmp_engine.dispose()
            logger.debug(_("PG ready (attempt {n})").format(n=_attempt))
            break
        except Exception:
            if _attempt < _max_wait:
                logger.debug(
                    _("⏳ PG not ready ({n}/{max}), retrying in 2s...").format(
                        n=_attempt, max=_max_wait
                    )
                )
                time.sleep(2)
            else:
                logger.error(
                    _(
                        "❌ Database not ready within 30s. Check Docker container status."
                    )
                )
                raise typer.Exit(code=1)

    try:
        indexer = VectorStoreManager(config)
        total_inserted = indexer.ingest(chunks)
        logger.info(
            _(
                "[green]✔[/green] Successfully wrote [bold blue]{count}[/bold blue] vectors to the database!"
            ).format(count=total_inserted)
        )
    except Exception as e:
        logger.error(_("❌ Vector ingestion failed: {err}").format(err=e))
        logger.warning(
            _(
                "💡 Hint: You may not have installed deps. Run `onebase get-deps > requirements.txt` then pip install."
            )
        )
        raise typer.Exit(code=1)


@app.command()
def serve(
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind the service"),
    detach: bool = typer.Option(
        False, "--detach", "-d", help="Run in background (detached mode)"
    ),
    with_ollama: bool = typer.Option(
        False, "--with-ollama", help="Bundle Ollama container with the service"
    ),
    with_xinference: bool = typer.Option(
        False,
        "--with-xinference",
        help="Bundle Xinference container (ModelScope ecosystem)",
    ),
    with_vllm: bool = typer.Option(
        False, "--with-vllm", help="Bundle vLLM container (max throughput)"
    ),
    with_docker_model: bool = typer.Option(
        False,
        "--with-docker-model",
        help="Use Docker Model Runner for inference (Docker Desktop 4.40+)",
    ),
    use_gpu: bool = typer.Option(
        False,
        "--use-gpu",
        "-g",
        help="Enable NVIDIA GPU passthrough for inference containers",
    ),
):
    """
    Start the OneBase service stack.
    """
    if not Path(CONFIG_FILE).exists():
        logger.error(_("❌ Config file not found. Run `onebase init` first."))
        raise typer.Exit(code=1)

    flags = sum([with_ollama, with_xinference, with_vllm, with_docker_model])
    if flags > 1:
        logger.error(
            _(
                "❌ Container conflict: only one local inference engine can be specified."
            )
        )
        raise typer.Exit(code=1)

    logger.info(_("🐳 Parsing config and preparing Docker services..."))

    try:
        config = OneBaseConfig.load(CONFIG_FILE)

        compute_mode = _("Host Machine")
        if with_ollama:
            compute_mode = _("Bundled Ollama")
        elif with_xinference:
            compute_mode = _("Bundled Xinference")
        elif with_vllm:
            compute_mode = _("Bundled vLLM")
        elif with_docker_model:
            compute_mode = _("Docker Model Runner")

        if use_gpu and flags > 0:
            compute_mode += " [bold green]+ NVIDIA GPU[/bold green]"

        table = Table(title=_("OneBase Status ({name})").format(name=config.site_name))
        table.add_column(_("Component"), style="cyan")
        table.add_column(_("Configuration"), style="magenta")
        table.add_row(
            _("Reasoning Engine"),
            f"{config.engine.reasoning.provider} / {config.engine.reasoning.model}",
        )
        table.add_row(_("Vector Store"), f"{config.database.vector_store}")
        table.add_row(_("Port"), str(port))
        table.add_row(_("Compute Mode"), compute_mode)

        console.print(table)

        if with_ollama:
            logger.info(
                _(
                    "💡 Ollama models will be pulled automatically on first container startup. "
                    "This may take a while depending on model size."
                )
            )
        elif with_xinference:
            logger.info(
                _(
                    "💡 Xinference models will be launched automatically on first container startup. "
                    "This may take a while depending on model size. "
                    "You can also visit `http://localhost:9997` to manage models."
                )
            )
        elif with_vllm:
            logger.info(
                _(
                    "💡 vLLM will automatically download model weights on first startup. "
                    "For gated models (Llama, Mistral, etc.), set HF_TOKEN in your .env file."
                )
            )
        elif with_docker_model:
            logger.info(
                _(
                    "💡 Docker Model Runner will pull and manage models natively. "
                    "Requires Docker Desktop 4.40+. Models are accessed via the built-in llama.cpp engine."
                )
            )

        runner = DockerRunner(
            config=config,
            port=port,
            with_ollama=with_ollama,
            with_xinference=with_xinference,
            with_vllm=with_vllm,
            with_docker_model=with_docker_model,
            use_gpu=use_gpu,
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=console,
        ) as progress:
            progress.add_task(
                description=_(
                    "🚀 Orchestrating containers and starting API service..."
                ),
                total=None,
            )
            runner.up(detach=detach)

        console.print(
            Panel.fit(
                _(
                    "🎉 OneBase is running!\n\n"
                    "🌐 URL: [bold underline cyan]http://localhost:{port}[/bold underline cyan]\n"
                    "🛑 Stop: run [bold red]onebase stop[/bold red]"
                ).format(port=port),
                title="Status: Online",
                border_style="green",
            )
        )
        if not detach:
            logger.info(
                _(
                    "📋 Logs: run [bold]docker compose -f .onebase/docker-compose.yml logs -f[/bold]"
                )
            )

    except Exception as e:
        logger.error(_("❌ Fatal error during startup: {err}").format(err=e))
        raise typer.Exit(code=1)


@app.command()
def stop(
    remove_volumes: bool = typer.Option(
        False,
        "--volumes",
        "-v",
        help="Also remove data volumes (WARNING: erases database and local model weights!)",
    ),
):
    """
    Gracefully stop and remove running OneBase services.
    """
    import subprocess

    compose_file = Path(HIDDEN_DIR) / "docker-compose.yml"

    if not compose_file.exists():
        logger.warning(
            _(
                "⚠️  No running service config found (.onebase/docker-compose.yml missing). Service may not be started."
            )
        )
        raise typer.Exit(code=0)

    logger.info(_("🛑 Stopping OneBase containers..."))

    cmd = ["docker", "compose", "-f", str(compose_file), "down"]

    if remove_volumes:
        logger.error(
            _(
                "⚠️  Warning: Cleaning up data volumes — database and local model weights will be erased!"
            )
        )
        cmd.append("-v")

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=console,
        ) as progress:
            progress.add_task(
                description=_("Sending SIGTERM and removing networks..."), total=None
            )
            logger.debug(f"Executing: {' '.join(cmd)}")
            subprocess.run(cmd, check=True, capture_output=True)

        logger.info(_("[green]✔[/green] Services stopped and cleaned up!"))
    except subprocess.CalledProcessError as e:
        logger.error(
            _("❌ Error stopping services: {err}").format(err=e.stderr.decode("utf-8"))
        )
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
