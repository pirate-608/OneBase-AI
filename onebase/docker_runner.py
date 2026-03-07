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
        with_docker_model: bool = False,
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
        self.with_docker_model = with_docker_model
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
        import re
        from .db import get_db_credentials, build_db_url

        creds = get_db_credentials()
        # Docker Compose 内部网络中，后端通过服务名 "db" 访问数据库
        db_url = build_db_url(host_override="db")

        # 用 site_name 生成项目隔离的卷名前缀，防止多项目共用同名卷导致凭据冲突
        _slug = re.sub(
            r"[^a-z0-9]+",
            "_",
            (self.config.site_name if self.config else "onebase").lower(),
        ).strip("_")
        vol_pg = f"{_slug}_pgdata"
        vol_ollama = f"{_slug}_ollama_data"
        vol_xinfer = f"{_slug}_xinference_data"
        vol_vllm = f"{_slug}_vllm_data"

        services = {}
        volumes_dict = {vol_pg: None}

        # 1. 数据库服务
        if self.config and self.config.database.type == "postgresql":
            services["db"] = {
                "image": "pgvector/pgvector:pg16",
                "restart": "always",
                "environment": {
                    "POSTGRES_USER": creds["user"],
                    "POSTGRES_PASSWORD": creds["password"],
                    "POSTGRES_DB": creds["dbname"],
                },
                "ports": [f"{creds['port']}:5432"],
                "volumes": [f"{vol_pg}:/var/lib/postgresql/data"],
                "healthcheck": {
                    "test": [
                        "CMD-SHELL",
                        f"pg_isready -U {creds['user']} -d {creds['dbname']}",
                    ],
                    "interval": "5s",
                    "timeout": "3s",
                    "retries": 10,
                    "start_period": "10s",
                },
            }

        # 2. 核心后端 API 服务
        if self.config:
            services["backend"] = {
                "restart": "always",
                "depends_on": {
                    "db": {"condition": "service_healthy"},
                },
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
                    "REDIS_CACHE_ENABLED": str(
                        self.config.performance.redis_cache_enabled
                    ).lower(),
                    "REDIS_CONTEXT_CACHE_TTL_SECONDS": str(
                        self.config.performance.redis_context_cache_ttl_seconds
                    ),
                    "RATE_LIMIT_ENABLED": str(
                        self.config.performance.rate_limit_enabled
                    ).lower(),
                    "CHAT_RATE_LIMIT_PER_MINUTE": str(
                        self.config.performance.chat_rate_limit_per_minute
                    ),
                    "UPLOAD_RATE_LIMIT_PER_MINUTE": str(
                        self.config.performance.upload_rate_limit_per_minute
                    ),
                    # 容器内标识，供 factory.py 自动重写 localhost → host.docker.internal
                    "RUNNING_IN_DOCKER": "true",
                    # 🔐 API Token 鉴权：从宿主机 .env 透传到容器
                    "API_TOKEN": "${API_TOKEN:-}",
                },
                "ports": [f"{self.port}:8000"],
                "volumes": ["../base:/app/base", "../onebase.yml:/app/onebase.yml"],
                "extra_hosts": ["host.docker.internal:host-gateway"],
                "healthcheck": {
                    "test": [
                        "CMD-SHELL",
                        "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')\"",
                    ],
                    "interval": "10s",
                    "timeout": "5s",
                    "retries": 5,
                    "start_period": "30s",
                },
                "deploy": {
                    "resources": {
                        "limits": {
                            "memory": "2G",
                        },
                    },
                },
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
                # Collect model names for auto-pull
                ollama_models_env = {}
                r_provider = self.config.engine.reasoning.provider.lower()
                e_provider = self.config.engine.embedding.provider.lower()
                if r_provider == "ollama":
                    ollama_models_env["OLLAMA_REASONING_MODEL"] = (
                        self.config.engine.reasoning.model
                    )
                if e_provider == "ollama":
                    ollama_models_env["OLLAMA_EMBEDDING_MODEL"] = (
                        self.config.engine.embedding.model
                    )

                services["ollama"] = {
                    "image": "ollama/ollama:latest",
                    "container_name": "onebase_ollama",
                    "ports": ["11434:11434"],
                    "volumes": [
                        f"{vol_ollama}:/root/.ollama",
                        "./backend/ollama-entrypoint.sh:/entrypoint.sh",
                    ],
                    "entrypoint": ["/bin/bash", "/entrypoint.sh"],
                    "environment": ollama_models_env,
                    "restart": "always",
                }
                if self.use_gpu:
                    services["ollama"]["deploy"] = self._get_gpu_deploy_block()

                services["backend"]["environment"][
                    "OLLAMA_BASE_URL"
                ] = "http://ollama:11434"
                services["backend"]["depends_on"]["ollama"] = {
                    "condition": "service_started"
                }
                volumes_dict[vol_ollama] = None

            elif self.with_xinference:
                # Collect model names for auto-launch
                xinference_models_env = {}
                r_provider = self.config.engine.reasoning.provider.lower()
                e_provider = self.config.engine.embedding.provider.lower()
                if r_provider == "xinference":
                    xinference_models_env["XINFERENCE_REASONING_MODEL"] = (
                        self.config.engine.reasoning.model
                    )
                if e_provider == "xinference":
                    xinference_models_env["XINFERENCE_EMBEDDING_MODEL"] = (
                        self.config.engine.embedding.model
                    )

                services["xinference"] = {
                    "image": "xprobe/xinference:latest",
                    "container_name": "onebase_xinference",
                    "ports": ["9997:9997"],
                    "volumes": [
                        f"{vol_xinfer}:/root/.xinference",
                        "./backend/xinference-entrypoint.sh:/entrypoint.sh",
                    ],
                    "entrypoint": ["/bin/bash", "/entrypoint.sh"],
                    "environment": xinference_models_env,
                    "restart": "always",
                }
                if self.use_gpu:
                    services["xinference"]["deploy"] = self._get_gpu_deploy_block()

                # 覆盖 OpenAI 协议接口为容器内部 Xinference 地址
                services["backend"]["environment"][
                    "OPENAI_API_BASE"
                ] = "http://xinference:9997/v1"
                services["backend"]["depends_on"]["xinference"] = {
                    "condition": "service_started"
                }
                volumes_dict[vol_xinfer] = None

            elif self.with_vllm:
                # 从配置文件读取模型名，传给 vLLM entrypoint
                model_name = self.config.engine.reasoning.model
                vllm_env = {"VLLM_MODEL_NAME": model_name}
                # 支持通过 .env 传入 HF_TOKEN 访问 gated 模型
                services["vllm"] = {
                    "image": "vllm/vllm-openai:latest",
                    "container_name": "onebase_vllm",
                    "ports": ["8001:8000"],
                    "volumes": [
                        f"{vol_vllm}:/root/.cache/huggingface",
                        "./backend/vllm-entrypoint.sh:/entrypoint.sh",
                    ],
                    "entrypoint": ["/bin/bash", "/entrypoint.sh"],
                    "environment": vllm_env,
                    "ipc": "host",
                    "restart": "always",
                }
                if self.use_gpu:
                    services["vllm"]["deploy"] = self._get_gpu_deploy_block()

                # 从 .env 注入 HF_TOKEN（如果存在）
                if not services["vllm"].get("env_file") and Path(".env").exists():
                    services["vllm"]["env_file"] = ["../.env"]

                # 覆盖 OpenAI 协议接口为容器内部 vLLM 地址 (vLLM 默认内部跑在 8000)
                services["backend"]["environment"][
                    "OPENAI_API_BASE"
                ] = "http://vllm:8000/v1"
                services["backend"]["depends_on"]["vllm"] = {
                    "condition": "service_started"
                }
                volumes_dict[vol_vllm] = None

            elif self.with_docker_model:
                # Docker Model Runner — 使用 Docker 原生模型管理 (Docker Desktop 4.40+)
                # 通过 provider 服务类型声明模型，Docker 自动拉取和管理
                docker_model_base_url = (
                    "http://model-runner.docker.internal/engines/llama.cpp/v1"
                )
                r_provider = self.config.engine.reasoning.provider.lower()
                e_provider = self.config.engine.embedding.provider.lower()

                if r_provider == "docker-model":
                    services["reasoning-model"] = {
                        "provider": {
                            "type": "model",
                            "options": {
                                "model": self.config.engine.reasoning.model,
                            },
                        },
                    }
                    services["backend"]["depends_on"]["reasoning-model"] = {
                        "condition": "service_started"
                    }

                if e_provider == "docker-model":
                    services["embedding-model"] = {
                        "provider": {
                            "type": "model",
                            "options": {
                                "model": self.config.engine.embedding.model,
                            },
                        },
                    }
                    services["backend"]["depends_on"]["embedding-model"] = {
                        "condition": "service_started"
                    }

                # 覆盖 OpenAI 协议接口为 Docker Model Runner 内部地址
                services["backend"]["environment"][
                    "OPENAI_API_BASE"
                ] = docker_model_base_url

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

        cmd = ["docker", "compose", "-f", str(self.compose_file), "up", "-d"]
        if not use_remote_image:
            cmd.append("--build")

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
