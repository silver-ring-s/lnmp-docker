# 迷你运维管理平台

一个基于 Flask + Docker 的轻量级运维管理平台，支持宿主机资源监控、容器生命周期管理、安全命令执行和系统日志查看。

## 功能

- **系统概览**：实时查看 CPU、内存、磁盘使用情况
- **容器管理**：列出所有 Docker 容器，支持启动/停止操作
- **命令执行**：通过 Web 安全执行预定义运维命令（磁盘、内存、网络等）
- **日志查看**：查看宿主机 syslog 最近 50 行日志

## 技术栈

- Python Flask
- Bootstrap 5 (CDN)
- Docker / Docker Compose
- Nginx 反向代理
- MySQL 数据持久化

## 快速开始

```bash
git clone https://github.com/你的用户名/lnmp-docker.git
cd lnmp-docker
docker compose up -d
# 访问 http://宿主机IP
架构说明
本项目采用 Docker Compose 编排三个核心服务：

┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│   Browser   │ ───>  │    Nginx     │ ───>  │  Flask App  │
│             │       │  (反向代理)  │       │  (运维后端) │
└─────────────┘       └──────────────┘       └──────┬──────┘
                                                    │
                                                    │ 读写
                                                    ▼
                                             ┌─────────────┐
                                             │    MySQL    │
                                             │  (数据存储) │
                                             └─────────────┘
容器与宿主机交互方式：

pid: "host"：共享宿主机 PID 命名空间，使 Flask 应用能通过 psutil 获取真实的主机 CPU、内存等指标。

挂载 /var/run/docker.sock：让容器内的 Docker CLI 可以直接管理宿主机的 Docker 引擎，实现容器列表查询、启停等操作。

只读挂载 /:/host：允许容器读取宿主机文件系统，用于查看系统日志 (/var/log/syslog)、获取真实磁盘使用率，以及通过 chroot /host 安全执行预定义命令。

项目结构

lnmp-docker/
├── docker-compose.yml        # 服务编排文件
├── flask-app/                # Flask 应用目录
│   ├── Dockerfile            # 应用镜像构建文件
│   ├── app.py                # 后端主逻辑
│   ├── requirements.txt      # Python 依赖
│   └── templates/            # 前端模板 (Bootstrap)
│       ├── base.html
│       ├── index.html
│       ├── containers.html
│       ├── commands.html
│       └── logs.html
├── nginx/
│   └── nginx.conf            # Nginx 反向代理配置
└── mysql/
    └── init.sql              # 数据库初始化脚本

安全设计
命令执行白名单：用户只能从预设列表中选择命令，参数完全由程序控制，杜绝任意命令注入。

chroot 隔离：执行命令时切换根目录至挂载的宿主机根目录，同时避免直接操作容器内文件系统。

只读挂载：宿主机根目录以只读方式挂载，防止误操作修改宿主机核心文件。

许可证
MIT

## 架构说明

本项目由三个 Docker 容器组成：

1. **Nginx**：反向代理，接收浏览器请求并转发给 Flask 后端
2. **Flask App**：运维管理后端，处理所有业务逻辑
3. **MySQL**：数据库，存储持久化数据

请求流程：Browser → Nginx (80端口) → Flask App (5000端口) → MySQL (3306端口)
