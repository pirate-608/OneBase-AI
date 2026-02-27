# 使用官方轻量级 Python 镜像
FROM python:3.11-slim-bookworm

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 复制前端构建生成的静态文件
COPY static ./static

# 暴露 FastAPI 运行的 8000 端口
EXPOSE 8000

# 启动 Uvicorn 服务器
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]