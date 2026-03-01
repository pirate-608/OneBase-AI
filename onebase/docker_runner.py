import yaml
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any

# 🌟 接入全局的日志和 UI 管理器
from .logger import logger, console
from .i18n import _


class DockerRunner:
    def __init__(
        self,
        config: Any,
        port: int,
        project_dir: str = ".onebase",
        with_ollama: bool = False,
        with_xinference: bool = False,
        with_vllm: bool = False,
        use_gpu: bool = False,
    ):
        self.config = config
        self.port = port
        self.project_dir = Path(project_dir)
        self.compose_file = self.project_dir / "docker-compose.yml"

        # 容器化推理服务标志
        self.with_ollama = with_ollama
        self.with_xinference = with_xinference
        self.with_vllm = with_vllm
        self.use_gpu = use_gpu

        self.package_dir = Path(__file__).parent.parent
        self.project_dir.mkdir(exist_ok=True)

        # 将静态的 self.console.print 彻底抽离，移交全域 logger 管理
        self.image_name = "pirate608/onebase-ai:latest"

    def _prepare_build_context(self):
        template_backend_dir = self.package_dir / "templates" / "backend"
        target_backend_dir = self.project_dir / "backend"

        shutil.copytree(template_backend_dir, target_backend_dir, dirs_exist_ok=True)
        factory_src = Path(__file__).parent / "factory.py"
        shutil.copy2(factory_src, target_backend_dir / "factory.py")

        frontend_dist_dir = self.package_dir / "templates" / "frontend" / "dist"
        target_static_dir = target_backend_dir / "static"

        if frontend_dist_dir.exists():
            shutil.copytree(frontend_dist_dir, target_static_dir, dirs_exist_ok=True)
        else:
            logger.warning(
                _(
                    "⚠️  Frontend build artifacts (dist) not found. "
                    "Run `npm run build` in templates/frontend first if you need the UI."
                )
            )

    def _get_gpu_deploy_block(self):
        """生成供 Docker Compose 识别的 NVIDIA GPU 穿透配置块"""
        return {
            "resources": {
                "reservations": {
                    "devices": [
                        {"driver": "nvidia", "count": "all", "capabilities": ["gpu"]}
                    ]
                }
            }
        }

    def _generate_compose_dict(self, use_remote_image: bool = False) -> Dict[str, Any]:
        # 🌟 [3-1] 数据库凭据从 .env 环境变量读取，不再硬编码
        import os
        from dotenv import load_dotenv

        load_dotenv()

        db_user = os.getenv("POSTGRES_USER", "onebase")
        db_pass = os.getenv("POSTGRES_PASSWORD", "onebase_secret")
        db_name = os.getenv("POSTGRES_DB", "onebase_db")
        db_url = f"postgresql+psycopg://{db_user}:{db_pass}@db:5432/{db_name}"

        services = {}
        volumes_dict = {"pgdata": None}

        # 1. 数据库服务
        if self.config and self.config.database.type == "postgresql":
            services["db"] = {
                "image": "pgvector/pgvector:pg16",
                "restart": "always",
                "environment": {
                    "POSTGRES_USER": db_user,
                    "POSTGRES_PASSWORD": db_pass,
                    "POSTGRES_DB": db_name,
                },
                "ports": ["5432:5432"],
                "volumes": ["pgdata:/var/lib/postgresql/data"],
            }

        # 2. 核心后端 API 服务
        if self.config:
            services["backend"] = {
                "restart": "always",
                "depends_on": ["db"],
                "environment": {
                    "DATABASE_URL": db_url,
                    "SITE_NAME": self.config.site_name,
                    "REASONING_PROVIDER": self.config.engine.reasoning.provider,
                    "REASONING_MODEL": self.config.engine.reasoning.model,
                    "EMBEDDING_PROVIDER": self.config.engine.embedding.provider,
                    "EMBEDDING_MODEL": self.config.engine.embedding.model,
                    # 🌟 [Step2] 将 feature flags 注入容器环境变量
                    "FEATURE_CHAT_HISTORY": str(
                        self.config.features.chat_history
                    ).lower(),
                    "FEATURE_FILE_UPLOAD": str(
                        self.config.features.file_upload
                    ).lower(),
                    # 默认网关穿透，指向宿主机上的各种推理服务端口
                    "OLLAMA_BASE_URL": "http://host.docker.internal:11434",
                    "OPENAI_API_BASE": "http://host.docker.internal:9997/v1",
                },
                "ports": [f"{self.port}:8000"],
                "volumes": ["../base:/app/base", "../onebase.yml:/app/onebase.yml"],
                "extra_hosts": ["host.docker.internal:host-gateway"],
            }

            if Path(".env").exists():
                services["backend"]["env_file"] = ["../.env"]

            if use_remote_image:
                services["backend"]["image"] = self.image_name
            else:
                services["backend"]["build"] = {
                    "context": "./backend",
                    "dockerfile": "Dockerfile",
                }

            # ==========================================
            # 🌟 3. 动态推理计算节点注入 (互斥)
            # ==========================================
            if self.with_ollama:
                services["ollama"] = {
                    "image": "ollama/ollama:latest",
                    "container_name": "onebase_ollama",
                    "ports": ["11434:11434"],
                    "volumes": ["ollama_data:/root/.ollama"],
                    "restart": "always",
                }
                if self.use_gpu:
                    services["ollama"]["deploy"] = self._get_gpu_deploy_block()

                services["backend"]["environment"][
                    "OLLAMA_BASE_URL"
                ] = "http://ollama:11434"
                services["backend"]["depends_on"].append("ollama")
                volumes_dict["ollama_data"] = None

            elif self.with_xinference:
                services["xinference"] = {
                    "image": "xprobe/xinference:latest",
                    "container_name": "onebase_xinference",
                    "ports": ["9997:9997"],
                    "volumes": ["xinference_data:/root/.xinference"],
                    "command": "xinference-local -H 0.0.0.0 -p 9997",
                    "restart": "always",
                }
                if self.use_gpu:
                    services["xinference"]["deploy"] = self._get_gpu_deploy_block()

                # 覆盖 OpenAI 协议接口为容器内部 Xinference 地址
                services["backend"]["environment"][
                    "OPENAI_API_BASE"
                ] = "http://xinference:9997/v1"
                services["backend"]["depends_on"].append("xinference")
                volumes_dict["xinference_data"] = None

            elif self.with_vllm:
                # 从配置文件读取模型名，传给 vLLM
                model_name = self.config.engine.reasoning.model
                services["vllm"] = {
                    "image": "vllm/vllm-openai:latest",
                    "container_name": "onebase_vllm",
                    "ports": ["8001:8000"],
                    "volumes": ["vllm_data:/root/.cache/huggingface"],
                    "command": f"--model {model_name} --host 0.0.0.0",
                    "ipc": "host",
                    "restart": "always",
                }
                if self.use_gpu:
                    services["vllm"]["deploy"] = self._get_gpu_deploy_block()

                # 覆盖 OpenAI 协议接口为容器内部 vLLM 地址 (vLLM 默认内部跑在 8000)
                services["backend"]["environment"][
                    "OPENAI_API_BASE"
                ] = "http://vllm:8000/v1"
                services["backend"]["depends_on"].append("vllm")
                volumes_dict["vllm_data"] = None

        return {"version": "3.8", "services": services, "volumes": volumes_dict}

    def build_compose_file(self, use_remote_image: bool = False):
        self._prepare_build_context()
        compose_dict = self._generate_compose_dict(use_remote_image)
        with open(self.compose_file, "w", encoding="utf-8") as f:
            yaml.dump(compose_dict, f, default_flow_style=False, sort_keys=False)

    def up(self, detach: bool = True):
        use_remote_image = False
        logger.info(
            _("[dim]🌐 Pulling pre-built image {image} (timeout: 15s)...[/dim]").format(
                image=self.image_name
            )
        )

        try:
            logger.debug(f"Executing: docker pull {self.image_name}")
            result = subprocess.run(
                ["docker", "pull", self.image_name],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if result.returncode == 0:
                use_remote_image = True
                logger.info(
                    _("[green]✅ Pre-built image pulled! Fast-start activated.[/green]")
                )
            else:
                logger.warning(
                    _(
                        "[yellow]⚠️ Image not published or pull failed. Falling back to local build.[/yellow]"
                    )
                )
        except subprocess.TimeoutExpired:
            logger.warning(
                _(
                    "[yellow]⚠️ Image pull timed out. Falling back to local build.[/yellow]"
                )
            )
        except Exception as e:
            logger.warning(
                _(
                    "[yellow]⚠️ Docker communication error ({err}). Falling back to local build.[/yellow]"
                ).format(err=e)
            )

        # 🌟 [2-4] 始终重新生成 compose 文件（带上最新的 use_remote_image 判断结果）
        # build 命令已单独调用过 build_compose_file()，但 serve 走 up() 入口时需要这里生成
        self.build_compose_file(use_remote_image)

        cmd = ["docker", "compose", "-f", str(self.compose_file), "up"]
        if not use_remote_image:
            cmd.append("--build")
        if detach:
            cmd.append("-d")

        try:
            logger.debug(f"Executing: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            raise RuntimeError(_("Docker Compose failed to start: {err}").format(err=e))

    def down(self, remove_volumes: bool = False):
        cmd = ["docker", "compose", "-f", str(self.compose_file), "down"]
        if remove_volumes:
            cmd.append("-v")

        logger.debug(f"Executing: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
