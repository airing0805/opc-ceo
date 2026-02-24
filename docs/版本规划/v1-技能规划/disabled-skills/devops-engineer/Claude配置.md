---
name: claude-code-setup
description: Claude Code 安装配置 - 安装、Skills 管理、配置文件
version: 1.0.0
parent: devops-engineer
---

# Claude Code 安装配置

## 安装 Claude Code

### npm 安装（推荐）

```bash
# 全局安装
npm install -g @anthropic-ai/claude-code

# 使用代理
npm install -g @anthropic-ai/claude-code --proxy http://127.0.0.1:7890

# 验证安装
claude --version
claude /help
```

### 更新 Claude Code

```bash
# 更新到最新版本
npm update -g @anthropic-ai/claude-code

# 安装特定版本
npm install -g @anthropic-ai/claude-code@0.x.x
```

## 配置文件位置

### 全局配置目录

```
Windows:
~/.claude/
├── settings.json        # 全局设置
├── rules/               # 规则文件
│   ├── common/          # 通用规则
│   ├── python/          # Python 规则
│   ├── typescript/      # TypeScript 规则
│   └── golang/          # Go 规则
├── skills/              # 技能文件
├── agents/              # 自定义 Agent
├── commands/            # 自定义命令
├── hooks/               # Hook 脚本
└── cache/               # 缓存目录
```

### 项目级配置

```
项目根目录/.claude/
├── settings.json        # 项目设置（覆盖全局）
├── CLAUDE.md           # 项目说明（重要！）
├── AGENTS.md           # Agent 说明
└── skills/             # 项目特定技能
```

## settings.json 配置

### 基础配置

```json
{
  "apiProvider": "anthropic",
  "defaultMode": "plan",
  "permissions": {
    "allow": [
      "Bash(*)",
      "Read(*)",
      "Write(*)",
      "Edit(*)"
    ]
  }
}
```

### 完整配置示例

```json
{
  "apiProvider": "anthropic",
  "defaultMode": "plan",
  
  "permissions": {
    "allow": [
      "Bash(npm *)",
      "Bash(git *)",
      "Bash(python *)",
      "Read(*)",
      "Write(.claude/**)",
      "Edit(src/**)"
    ],
    "deny": [
      "Bash(rm -rf /)",
      "Bash(format *)"
    ]
  },
  
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": ["echo 'Executing command...'"]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": ["echo 'File created'"]
      }
    ]
  },
  
  "env": {
    "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"
  },
  
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\Projects"]
    }
  }
}
```

### 配置项说明

| 配置项 | 说明 | 可选值 |
|--------|------|--------|
| `apiProvider` | API 提供商 | `anthropic`, `openai` |
| `defaultMode` | 默认模式 | `plan`, `accept`, `auto` |
| `permissions.allow` | 允许的操作 | 工具匹配模式 |
| `permissions.deny` | 禁止的操作 | 工具匹配模式 |
| `hooks` | 钩子配置 | PreToolUse, PostToolUse |
| `env` | 环境变量 | 变量映射 |
| `mcpServers` | MCP 服务器 | 服务器配置 |

## Skills（技能）管理

### 安装 Skills

```bash
# 方式 1：从 GitHub 克隆
git clone https://github.com/affaan-m/everything-claude-code ~/.claude/skills/ecc

# 方式 2：手动添加
# 将 .md 文件放入 ~/.claude/skills/ 目录

# 方式 3：项目级 skills
# 将 .md 文件放入 项目/.claude/skills/ 目录
```

### 常用 Skills 推荐

#### Python 开发
- `python-patterns` - Python 最佳实践
- `python-testing` - pytest 测试指南
- `django-patterns` - Django 框架模式

#### TypeScript/前端
- `frontend-patterns` - 前端开发模式
- `coding-standards` - 代码规范

#### 后端开发
- `backend-patterns` - 后端架构模式
- `api-design` - REST API 设计
- `postgres-patterns` - PostgreSQL 最佳实践

#### 测试
- `tdd-workflow` - 测试驱动开发
- `e2e-testing` - E2E 测试指南

#### 安全
- `security-review` - 安全审查
- `django-security` - Django 安全

#### 部署
- `docker-patterns` - Docker 模式
- `deployment-patterns` - 部署模式

### 安装 Everything Claude Code

```bash
# 克隆仓库
git clone https://github.com/affaan-m/everything-claude-code.git
cd everything-claude-code

# 安装 rules
cp -r rules/common ~/.claude/rules/
cp -r rules/python ~/.claude/rules/
cp -r rules/typescript ~/.claude/rules/

# 安装 skills
cp -r skills/* ~/.claude/skills/

# 安装 agents
cp -r agents/* ~/.claude/agents/
```

## Rules（规则）配置

### 规则文件结构

```
~/.claude/rules/
├── common/              # 通用规则
│   ├── coding-style.md
│   ├── git-workflow.md
│   ├── testing.md
│   ├── performance.md
│   ├── patterns.md
│   ├── hooks.md
│   ├── agents.md
│   └── security.md
├── python/              # Python 特定
├── typescript/          # TypeScript 特定
└── golang/              # Go 特定
```

### 规则示例

```markdown
# Coding Style

## Immutability (CRITICAL)

ALWAYS create new objects, NEVER mutate existing ones:
- Use spread operator: `{...obj, newField: value}`
- Use map/filter: `arr.map(x => x * 2)`

## File Organization

- High cohesion, low coupling
- 200-400 lines typical, 800 max
- Organize by feature/domain
```

## Agents（代理）配置

### 自定义 Agent

```markdown
---
name: my-custom-agent
description: Custom agent for specific tasks
tools:
  - Read
  - Write
  - Bash
---

# My Custom Agent

Specialized for handling specific tasks...

## Instructions
...
```

### Agent 配置位置

```
~/.claude/agents/
├── planner.md
├── code-reviewer.md
├── tdd-guide.md
└── my-custom-agent.md
```

## MCP 服务器配置

### 安装 MCP 服务器

```bash
# 文件系统 MCP
npm install -g @modelcontextprotocol/server-filesystem

# GitHub MCP
npm install -g @modelcontextprotocol/server-github

# SQLite MCP
npm install -g @modelcontextprotocol/server-sqlite
```

### 配置 MCP 服务器

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\Projects"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      }
    }
  }
}
```

## 常用命令

```bash
# 启动 Claude Code
claude

# 指定工作目录
claude --cwd /path/to/project

# 查看帮助
claude /help

# 查看版本
claude --version

# 设置 API Key
claude config set apiKey YOUR_API_KEY

# 清除缓存
rm -rf ~/.claude/cache

# 查看日志
# Windows: %APPDATA%\claude-code\logs\
# Mac/Linux: ~/.claude-code/logs/
```

## 故障排查

### 常见问题

```bash
# 1. API Key 问题
echo $ANTHROPIC_API_KEY
claude config set apiKey $ANTHROPIC_API_KEY

# 2. 权限问题
# 检查 settings.json 中的 permissions 配置

# 3. 网络问题
# 配置代理
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890

# 4. 缓存问题
rm -rf ~/.claude/cache

# 5. 版本问题
claude --version
npm update -g @anthropic-ai/claude-code
```
