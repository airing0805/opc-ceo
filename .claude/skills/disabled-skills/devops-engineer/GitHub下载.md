---
name: github-download
description: GitHub 项目下载 - 克隆、认证、Release 下载
version: 1.0.0
parent: devops-engineer
---

# GitHub 项目下载

## 默认配置

> **默认下载目录**: `E:\repository_git`
>
> 所有 Git 项目默认克隆到此目录，保持项目组织有序。

### 目录结构建议

```
E:\repository_git\
├── github\              # GitHub 项目
│   ├── 用户名\          # 按作者分类
│   └── ...
├── gitee\               # Gitee 项目
├── work\                # 工作项目
└── personal\            # 个人项目
```

### 快速切换到默认目录

```powershell
# PowerShell 别名（添加到 $PROFILE）
function cdt { Set-Location "E:\repository_git" }

# 或使用别名
Set-Alias -Name repos -Value "E:\repository_git"
```

### 克隆到默认目录

```bash
# 标准方式：先切换目录再克隆
cd E:\repository_git
git clone https://github.com/用户名/仓库名.git

# 或直接指定完整路径
git clone https://github.com/用户名/仓库名.git E:\repository_git\仓库名

# 使用 gh CLI
cd E:\repository_git
gh repo clone 用户名/仓库名
```

## 基础克隆命令

### HTTPS 克隆（推荐，最通用）

```bash
git clone https://github.com/用户名/仓库名.git
```

### SSH 克隆（需要配置 SSH 密钥）

```bash
git clone git@github.com:用户名/仓库名.git
```

### GitHub CLI 克隆（推荐，自动处理认证）

```bash
gh repo clone 用户名/仓库名
```

## 常用克隆选项

### 浅克隆（节省空间和时间）

```bash
# 只克隆最近一次提交
git clone --depth 1 https://github.com/用户名/仓库名.git

# 克隆最近 N 次提交
git clone --depth 10 https://github.com/用户名/仓库名.git
```

### 克隆特定分支

```bash
# 克隆指定分支
git clone --branch 分支名 https://github.com/用户名/仓库名.git

# 浅克隆特定分支（推荐用于 CI/CD）
git clone --branch 分支名 --single-branch --depth 1 https://github.com/用户名/仓库名.git
```

### 克隆特定标签

```bash
git clone --branch v1.0.0 https://github.com/用户名/仓库名.git
```

### 稀疏检出（只下载需要的目录）

```bash
git clone --filter=blob:none --sparse https://github.com/用户名/仓库名.git
cd 仓库名
git sparse-checkout set 目录1 目录2
```

### 指定目标目录

```bash
git clone https://github.com/用户名/仓库名.git 自定义目录名
```

## 私有仓库认证

### 使用 Personal Access Token（HTTPS）

```bash
# 方式 1：在 URL 中包含 token
git clone https://<token>@github.com/用户名/私有仓库.git

# 方式 2：配置 credential helper（推荐）
git config --global credential.helper store
git clone https://github.com/用户名/私有仓库.git
# 输入用户名和 token
```

### 使用 GitHub CLI（推荐）

```bash
# 先登录
gh auth login

# 然后正常克隆，自动处理认证
gh repo clone 用户名/私有仓库
```

### 使用 SSH 密钥

```bash
# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 添加到 ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 将公钥添加到 GitHub Settings > SSH Keys

# 克隆
git clone git@github.com:用户名/私有仓库.git
```

## 下载 Release 文件

### 使用 GitHub CLI

```bash
# 列出所有 releases
gh release list --repo 用户名/仓库名

# 下载最新 release 的所有文件
gh release download --repo 用户名/仓库名

# 下载特定版本
gh release download v1.0.0 --repo 用户名/仓库名

# 下载特定文件
gh release download v1.0.0 --repo 用户名/仓库名 --pattern "*.zip"
```

### 直接下载压缩包（不克隆）

```bash
# 下载 ZIP
curl -LO https://github.com/用户名/仓库名/archive/refs/heads/main.zip

# 下载 TAR.GZ
curl -LO https://github.com/用户名/仓库名/archive/refs/heads/main.tar.gz

# 下载特定标签
curl -LO https://github.com/用户名/仓库名/archive/refs/tags/v1.0.0.zip
```

### 使用 wget 下载

```bash
wget https://github.com/用户名/仓库名/archive/main.zip
```

## Fork 仓库后同步上游

```bash
# 添加上游仓库
git remote add upstream https://github.com/原作者/原仓库.git

# 获取上游更新
git fetch upstream

# 合并到本地
git checkout main
git merge upstream/main

# 推送到自己的 fork
git push origin main
```

## 常用场景

### 场景 1：快速下载项目源码（不需要 git 历史）

```bash
# 使用 gh CLI
gh repo clone 用户名/仓库名 -- --depth 1

# 或者直接下载 ZIP
curl -LO https://github.com/用户名/仓库名/archive/main.zip
unzip main.zip
```

### 场景 2：只下载特定目录

```bash
git clone --filter=blob:none --sparse https://github.com/用户名/仓库名.git
cd 仓库名
git sparse-checkout set src/components docs
```

### 场景 3：下载指定版本的 Release

```bash
# 查看 releases
gh release list --repo 用户名/仓库名

# 下载指定版本
gh release download v2.0.0 --repo 用户名/仓库名
```
