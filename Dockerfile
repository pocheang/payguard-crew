# 后端 Dockerfile - 优化版本
FROM python:3.11-slim as base

# 构建参数
ARG BUILD_DATE
ARG VERSION=0.2.0

# 元数据标签
LABEL maintainer="PayGuard Team"
LABEL version="${VERSION}"
LABEL build_date="${BUILD_DATE}"
LABEL description="PayGuard Risk Control System Backend"

WORKDIR /app

# Python环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 依赖阶段（利用Docker缓存）
FROM base as dependencies

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 最终阶段
FROM dependencies as final

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p data logs .chroma docs && \
    echo "# PayGuard Documentation" > docs/README.md && \
    chmod -R 755 data logs .chroma docs

# 创建非root用户（安全最佳实践）
RUN useradd -m -u 1000 payguard && \
    chown -R payguard:payguard /app

# 切换到非root用户
USER payguard

EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/api/health/health || exit 1

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
