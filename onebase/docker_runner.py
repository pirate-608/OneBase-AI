import yaml
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any
from rich.console import Console # 🌟 新增用于打印优雅的提示信息

class DockerRunner:
    def __init__(self, config: Any, port: int, project_dir: str = ".onebase"):
        self.config = config
        self.port = port
        self.project_dir = Path(project_dir)
        self.compose_file = self.project_dir / "docker-compose.yml"
        
        # 获取 onebase 工具自身的根目录，以便找到 templates
        self.package_dir = Path(__file__).parent.parent
        self.project_dir.mkdir(exist_ok=True)
        
        self.console = Console()
        # ⚠️ 请将这里的 username 替换为你真实的 Docker Hub 账户名
        self.image_name = "pirate-608/onebase-ai:latest"

    def _prepare_build_context(self):
        """将后端代码与前端静态资源组装在一起，准备给 Docker 构建"""
        template_backend_dir = self.package_dir / "templates" / "backend"
        target_backend_dir = self.project_dir / "backend"

        # 1. 拷贝后端模板代码 (main.py, Dockerfile 等)
        shutil.copytree(template_backend_dir, target_backend_dir, dirs_exist_ok=True)

        # 2. 将外层的 factory.py 动态拷贝进后端的 Docker 构建目录中
        factory_src = Path(__file__).parent / "factory.py"
        shutil.copy2(factory_src, target_backend_dir / "factory.py")

        # 3. 拷贝前端打包产物 (dist -> static)
        frontend_dist_dir = self.package_dir / "templates" / "frontend" / "dist"
        target_static_dir = target_backend_dir / "static"

        if frontend_dist_dir.exists():
            shutil.copytree(frontend_dist_dir, target_static_dir, dirs_exist_ok=True)
        else:
            print("⚠️ 警告：未找到前端构建产物(dist)。如果你需要 UI 界面，请先在 templates/frontend 执行 npm run build")
            
    # 🌟 新增参数 use_remote_image，根据结果生成不同的 docker-compose 结构
    def _generate_compose_dict(self, use_remote_image: bool = False) -> Dict[str, Any]:
        """将 OneBaseConfig 转换为 docker-compose 的字典结构"""
        db_user = "onebase"
        db_pass = "onebase_secret"
        db_name = "onebase_db"
        db_url = f"postgresql+psycopg://{db_user}:{db_pass}@db:5432/{db_name}"
        
        services = {}

        # 1. 数据库服务 (保持不变)
        if self.config.database.type == "postgresql":
            services["db"] = {
                "image": "pgvector/pgvector:pg16",
                "restart": "always",
                "environment": {
                    "POSTGRES_USER": db_user,
                    "POSTGRES_PASSWORD": db_pass,
                    "POSTGRES_DB": db_name,
                },
                "ports": ["5432:5432"],
                "volumes": ["pgdata:/var/lib/postgresql/data"]
            }

        # 2. 后端 API 服务通用配置
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
                "OLLAMA_BASE_URL": "http://host.docker.internal:11434"
            },
            "ports": [f"{self.port}:8000"],
            "volumes": [
                "../base:/app/base",
                "../onebase.yml:/app/onebase.yml"
            ]
        }
        
        if Path(".env").exists():
            services["backend"]["env_file"] = ["../.env"]

        # 🌟 核心分发逻辑：如果有远程镜像就用 image，否则用 build
        if use_remote_image:
            services["backend"]["image"] = self.image_name
        else:
            services["backend"]["build"] = {
                "context": "./backend",
                "dockerfile": "Dockerfile"
            }

        return {
            "version": "3.8",
            "services": services,
            "volumes": {"pgdata": None}
        }

    def build_compose_file(self, use_remote_image: bool = False):
        """拷贝源码，并根据策略生成 docker-compose.yml"""
        # 无论是否使用远程镜像，都准备一份本地构建上下文以防万一
        self._prepare_build_context() 
        
        compose_dict = self._generate_compose_dict(use_remote_image)
        with open(self.compose_file, "w", encoding="utf-8") as f:
            yaml.dump(compose_dict, f, default_flow_style=False, sort_keys=False)

    def up(self, detach: bool = True):
        # 🌟 第一步：尝试 15 秒拉取远程镜像
        use_remote_image = False
        self.console.print(f"[dim]🌐 尝试拉取预编译云端镜像 {self.image_name} (超时: 15s)...[/dim]")
        try:
            result = subprocess.run(
                ["docker", "pull", self.image_name],
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0:
                use_remote_image = True
                self.console.print("[green]✅ 预编译镜像拉取成功！触发极速启动。[/green]")
            else:
                self.console.print("[yellow]⚠️ 镜像未发布或拉取失败，智能回退至本地构建模式。[/yellow]")
        except subprocess.TimeoutExpired:
            self.console.print("[yellow]⚠️ 镜像拉取超时，智能回退至本地构建模式。[/yellow]")
        except Exception:
            self.console.print("[yellow]⚠️ Docker 通信异常，智能回退至本地构建模式。[/yellow]")

        # 🌟 第二步：根据结果生成 Compose 并执行启动
        self.build_compose_file(use_remote_image)
        
        cmd = ["docker", "compose", "-f", str(self.compose_file), "up"]
        
        # 只有在本地构建模式下，才强制 --build，节省时间
        if not use_remote_image:
            cmd.append("--build")
            
        if detach:
            cmd.append("-d")
            
        try:
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Docker Compose 启动失败: {e}")
        except FileNotFoundError:
            raise RuntimeError("找不到 docker 命令，请确保已安装 Docker Desktop 或 Docker Engine。")

    def down(self):
        """执行 docker compose down"""
        cmd = ["docker", "compose", "-f", str(self.compose_file), "down"]
        subprocess.run(cmd, check=True)