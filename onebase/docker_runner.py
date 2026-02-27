import yaml
import subprocess
import shutil # 新增
from pathlib import Path
from typing import Dict, Any

class DockerRunner:
    def __init__(self, config: Any, port: int, project_dir: str = ".onebase"):
        self.config = config
        self.port = port
        self.project_dir = Path(project_dir)
        self.compose_file = self.project_dir / "docker-compose.yml"
        
        # 获取 onebase 工具自身的根目录，以便找到 templates
        # 这里假设 docker_runner.py 位于 onebase/ 目录下
        self.package_dir = Path(__file__).parent.parent
        
        self.project_dir.mkdir(exist_ok=True)

    def _prepare_build_context(self):
        """将后端代码与前端静态资源组装在一起，准备给 Docker 构建"""
        template_backend_dir = self.package_dir / "templates" / "backend"
        target_backend_dir = self.project_dir / "backend"

        import shutil
        
        # 1. 拷贝后端模板代码 (main.py, Dockerfile 等)
        shutil.copytree(template_backend_dir, target_backend_dir, dirs_exist_ok=True)

        # 🚀【核心缝合】：将外层的 factory.py 动态拷贝进后端的 Docker 构建目录中！
        factory_src = Path(__file__).parent / "factory.py"
        shutil.copy2(factory_src, target_backend_dir / "factory.py")

        # 2. 拷贝前端打包产物 (dist -> static)
        frontend_dist_dir = self.package_dir / "templates" / "frontend" / "dist"
        target_static_dir = target_backend_dir / "static"

        if frontend_dist_dir.exists():
            shutil.copytree(frontend_dist_dir, target_static_dir, dirs_exist_ok=True)
        else:
            print("⚠️ 警告：未找到前端构建产物(dist)。如果你需要 UI 界面，请先在 templates/frontend 执行 npm run build")
            
    def _generate_compose_dict(self) -> Dict[str, Any]:
        """将 OneBaseConfig 转换为 docker-compose 的字典结构"""
        
        db_user = "onebase"
        db_pass = "onebase_secret"
        db_name = "onebase_db"
        # 确保这里带有 +psycopg
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

        # 2. 后端 API 服务
        services["backend"] = {
            "build": {
                "context": "./backend",
                "dockerfile": "Dockerfile"
            },
            "restart": "always",
            "depends_on": ["db"],
            "environment": {
                "DATABASE_URL": db_url,
                "SITE_NAME": self.config.site_name,
                "REASONING_PROVIDER": self.config.engine.reasoning.provider,
                "REASONING_MODEL": self.config.engine.reasoning.model,
                "EMBEDDING_PROVIDER": self.config.engine.embedding.provider,
                "EMBEDDING_MODEL": self.config.engine.embedding.model,
                # 🚀【核心缝合】：为未来可能切回 Ollama 铺平道路
                "OLLAMA_BASE_URL": "http://host.docker.internal:11434"
            },
            "ports": [f"{self.port}:8000"],
            # 🌟 新增：不仅挂载 base 目录，还要挂载 onebase.yml 配置文件
            "volumes": [
                "../base:/app/base",
                "../onebase.yml:/app/onebase.yml"
            ]
        }
        
        if Path(".env").exists():
            services["backend"]["env_file"] = ["../.env"]

        return {
            "version": "3.8",
            "services": services,
            "volumes": {"pgdata": None}
        }

    def build_compose_file(self):
        """拷贝源码，并生成 docker-compose.yml"""
        self._prepare_build_context() # 触发拷贝逻辑
        
        compose_dict = self._generate_compose_dict()
        with open(self.compose_file, "w", encoding="utf-8") as f:
            yaml.dump(compose_dict, f, default_flow_style=False, sort_keys=False)

    def up(self, detach: bool = True):
        self.build_compose_file()
        
        # 核心改动：加上 --build 参数，强制 Docker 每次启动时检查并重新构建镜像
        cmd = ["docker", "compose", "-f", str(self.compose_file), "up", "--build"]
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