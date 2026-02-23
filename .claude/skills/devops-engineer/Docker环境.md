---
name: docker-environment
description: Docker 环境 - 安装、常用命令、镜像加速
version: 1.0.0
parent: devops-engineer
---

# Docker 环境

## 安装 Docker Desktop

### Windows 安装

```powershell
# 使用 winget 安装
winget install Docker.DockerDesktop

# 使用 Chocolatey 安装
choco install docker-desktop -y

# 手动下载
# https://www.docker.com/products/docker-desktop
```

### 前置要求

- Windows 10/11 64位
- 启用 WSL 2 或 Hyper-V
- BIOS 中启用虚拟化

### 启用 WSL 2（推荐）

```powershell
# 以管理员运行
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# 重启后，设置 WSL 2 为默认
wsl --set-default-version 2

# 安装 Linux 发行版
wsl --install -d Ubuntu
```

### Linux 安装

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh

# 将当前用户加入 docker 组
sudo usermod -aG docker $USER

# 启动服务
sudo systemctl enable docker
sudo systemctl start docker
```

### 验证安装

```bash
# 查看版本
docker --version
docker compose version

# 运行测试容器
docker run hello-world

# 查看 Docker 信息
docker info
```

## 镜像加速

### 配置镜像加速器

编辑 Docker Desktop 设置或 `/etc/docker/daemon.json`：

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ],
  "insecure-registries": [],
  "debug": false,
  "experimental": false
}
```

### Windows Docker Desktop 配置

1. 打开 Docker Desktop
2. Settings > Docker Engine
3. 编辑 JSON 配置
4. Apply & Restart

## 镜像管理

### 搜索和获取镜像

```bash
# 搜索镜像
docker search nginx
docker search python --filter=stars=100

# 拉取镜像
docker pull nginx
docker pull nginx:1.25
docker pull python:3.12-slim

# 拉取所有标签
docker pull --all-tags nginx

# 从其他仓库拉取
docker pull gcr.io/project/image:tag
docker pull quay.io/organization/image:tag
```

### 查看镜像

```bash
# 列出本地镜像
docker images
docker image ls

# 查看镜像详情
docker image inspect nginx

# 查看镜像历史
docker history nginx

# 查看镜像层
docker image inspect nginx --format='{{json .RootFS.Layers}}'
```

### 删除镜像

```bash
# 删除镜像
docker rmi nginx
docker image rm nginx

# 强制删除
docker rmi -f nginx

# 删除所有未使用的镜像
docker image prune
docker image prune -a  # 删除所有未使用的

# 删除悬空镜像
docker image prune -f
```

### 镜像导入导出

```bash
# 导出镜像
docker save -o nginx.tar nginx:latest
docker save nginx:latest | gzip > nginx.tar.gz

# 导入镜像
docker load -i nginx.tar
docker load < nginx.tar.gz

# 从容器创建镜像
docker commit container_name myimage:v1

# 使用 Dockerfile 构建镜像
docker build -t myimage:v1 .
docker build -t myimage:v1 -f Dockerfile.prod .
```

## 容器管理

### 运行容器

```bash
# 基础运行
docker run nginx

# 后台运行
docker run -d nginx

# 指定名称
docker run -d --name my-nginx nginx

# 端口映射
docker run -d -p 8080:80 nginx
docker run -d -p 127.0.0.1:8080:80 nginx

# 挂载卷
docker run -d -v /host/path:/container/path nginx
docker run -d -v $(pwd):/app nginx

# 环境变量
docker run -d -e MYSQL_ROOT_PASSWORD=secret mysql

# 组合使用
docker run -d \
  --name my-app \
  -p 8080:80 \
  -v $(pwd)/data:/data \
  -e NODE_ENV=production \
  myimage:latest
```

### 查看容器

```bash
# 查看运行中的容器
docker ps
docker container ls

# 查看所有容器
docker ps -a

# 查看容器详情
docker inspect container_name

# 查看容器进程
docker top container_name

# 查看容器资源使用
docker stats container_name
docker stats  # 所有容器
```

### 容器操作

```bash
# 启动/停止/重启
docker start container_name
docker stop container_name
docker restart container_name

# 暂停/恢复
docker pause container_name
docker unpause container_name

# 进入容器
docker exec -it container_name bash
docker exec -it container_name sh

# 在容器中执行命令
docker exec container_name ls /app
docker exec container_name cat /etc/hosts

# 查看日志
docker logs container_name
docker logs -f container_name  # 实时
docker logs --tail 100 container_name
docker logs --since 2h container_name

# 复制文件
docker cp file.txt container_name:/path/
docker cp container_name:/path/file.txt ./
```

### 删除容器

```bash
# 删除容器
docker rm container_name

# 强制删除运行中的容器
docker rm -f container_name

# 删除所有停止的容器
docker container prune

# 删除所有容器
docker rm -f $(docker ps -aq)
```

## Docker Compose

### 基础命令

```bash
# 启动服务
docker-compose up
docker-compose up -d  # 后台运行

# 停止服务
docker-compose down
docker-compose down -v  # 同时删除卷

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs
docker-compose logs -f service_name

# 重启服务
docker-compose restart

# 重新构建
docker-compose build
docker-compose up --build
```

### docker-compose.yml 示例

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=1
    volumes:
      - ./:/app
    depends_on:
      - db
      - redis
    
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## 网络管理

### 网络类型

| 类型 | 说明 |
|------|------|
| bridge | 默认网络，容器间通信 |
| host | 使用主机网络 |
| none | 无网络 |
| overlay | 跨主机网络 |

### 网络命令

```bash
# 列出网络
docker network ls

# 创建网络
docker network create mynetwork
docker network create --driver bridge mynetwork

# 连接容器到网络
docker network connect mynetwork container_name

# 断开连接
docker network disconnect mynetwork container_name

# 查看网络详情
docker network inspect mynetwork

# 删除网络
docker network rm mynetwork

# 删除未使用的网络
docker network prune
```

## 数据卷管理

### 数据卷命令

```bash
# 列出卷
docker volume ls

# 创建卷
docker volume create myvolume

# 查看卷详情
docker volume inspect myvolume

# 删除卷
docker volume rm myvolume

# 删除未使用的卷
docker volume prune

# 备份卷
docker run --rm -v myvolume:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz /data

# 恢复卷
docker run --rm -v myvolume:/data -v $(pwd):/backup alpine tar xzf /backup/backup.tar.gz -C /
```

## 清理命令

```bash
# 清理所有未使用的资源
docker system prune

# 清理所有（包括未使用的镜像）
docker system prune -a

# 清理卷
docker volume prune

# 清理网络
docker network prune

# 清理容器
docker container prune

# 清理镜像
docker image prune -a

# 查看磁盘使用
docker system df
docker system df -v
```

## 常用场景

### 运行数据库

```bash
# MySQL
docker run -d \
  --name mysql \
  -e MYSQL_ROOT_PASSWORD=secret \
  -e MYSQL_DATABASE=mydb \
  -p 3306:3306 \
  -v mysql_data:/var/lib/mysql \
  mysql:8

# PostgreSQL
docker run -d \
  --name postgres \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=mydb \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15

# Redis
docker run -d \
  --name redis \
  -p 6379:6379 \
  -v redis_data:/data \
  redis:7-alpine

# MongoDB
docker run -d \
  --name mongodb \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=secret \
  -p 27017:27017 \
  -v mongo_data:/data/db \
  mongo:7
```

### 运行 Web 服务

```bash
# Nginx
docker run -d \
  --name nginx \
  -p 80:80 \
  -p 443:443 \
  -v $(pwd)/html:/usr/share/nginx/html \
  -v $(pwd)/conf.d:/etc/nginx/conf.d \
  nginx:latest

# Node.js 应用
docker run -d \
  --name node-app \
  -p 3000:3000 \
  -v $(pwd):/app \
  -w /app \
  node:20 \
  npm start
```

### 一键部署开发环境

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - ./:/app
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/mydb
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - db_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  adminer:
    image: adminer
    ports:
      - "8080:8080"

volumes:
  db_data:
```
