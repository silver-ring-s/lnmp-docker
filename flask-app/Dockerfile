FROM python:3.10-slim

# 安装系统工具 + Docker 命令行
RUN apt-get update && apt-get install -y --no-install-recommends \
    procps \
    util-linux \
    net-tools \
    iputils-ping \
    traceroute \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]



























