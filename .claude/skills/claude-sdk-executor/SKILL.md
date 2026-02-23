---
name: claude-sdk-executor
description: 通过 Claude Agent SDK 进行会话管理和任务执行
version: 3.0.0
source: local-creation
author: OPC-CEO
---

# Claude SDK 执行器

## 角色定位

通过 Claude Agent SDK (`claude-agent-sdk`) 进行会话管理和任务执行的执行层。

## 核心能力

- **列出会话** - 查看项目的历史会话列表
- **恢复会话** - 恢复之前的会话，保留上下文
- **执行任务** - 在会话中执行任务（自动保存历史）
- **管理项目** - 查看所有有历史记录的项目

## 会话存储

Claude Code 的会话历史存放在：
```
~/.claude/projects/<project_hash>/<session_id>.jsonl
```

- `project_hash` - 根据项目路径生成的 MD5 哈希（前 16 位）
- `session_id.jsonl` - JSONL 格式的会话历史文件

## 能力边界

| 可以做 | 不能做 |
|--------|--------|
| SDK 会话管理 | 业务决策 |
| 跨会话任务执行 | 用户交互 |
| 读取历史消息 | 跨角色协调 |

## 文件结构

```
.claude/skills/claude-sdk-executor/
├── SKILL.md           # 技能文档
└── scripts/           # Python 脚本目录
    ├── sessions.py    # 会话管理脚本
    └── pyproject.toml # uv 依赖配置
```

## 安装依赖

```bash
cd .claude/skills/claude-sdk-executor/scripts
uv sync
```

## 操作命令

### 命令 1：列出项目会话

**用途**：查看指定项目的历史会话

**语法**：
```bash
cd .claude/skills/claude-sdk-executor/scripts && uv run sessions.py list --cwd <project_path>
```

**参数**：

| 参数 | 说明 |
|------|------|
| `--cwd <path>` | 项目目录（必需） |

**示例**：
```bash
# 列出项目的历史会话
uv run sessions.py list --cwd E:/my-project
```

**输出示例**：
```json
{
  "sessions": [
    {
      "id": "sess_abc123",
      "title": "分析项目结构...",
      "timestamp": "2026-02-23T10:00:00",
      "message_count": 12,
      "cwd": "E:/my-project",
      "tools": ["Read", "Glob", "Grep"]
    }
  ],
  "count": 1
}
```

---

### 命令 2：列出所有项目

**用途**：查看所有有历史记录的项目

**语法**：
```bash
uv run sessions.py projects
```

---

### 命令 3：获取会话详情

**用途**：查看指定会话的详细信息

**语法**：
```bash
uv run sessions.py get <session_id>
```

---

### 命令 4：执行任务

**用途**：创建新会话或恢复会话执行任务

**语法**：
```bash
uv run sessions.py exec "<prompt>" [options]
```

**参数**：

| 参数 | 说明 |
|------|------|
| `<prompt>` | 任务提示（必需） |
| `--cwd <path>` | 工作目录 |
| `--resume <session_id>` | 恢复指定会话 |
| `--tools <tool1,tool2>` | 允许的工具（默认: Read,Glob,Grep,Bash） |

**示例**：

```bash
# 创建新会话执行任务
uv run sessions.py exec "分析这个项目的结构" --cwd E:/my-project

# 恢复会话继续任务
uv run sessions.py exec "继续分析" --resume sess_abc123
```

---

### 命令 5：删除会话

**用途**：删除会话历史文件

**语法**：
```bash
uv run sessions.py delete <session_id>
```

---

## 典型工作流

### 工作流 1：查看历史

```bash
# 1. 列出项目的历史会话
uv run sessions.py list --cwd E:/my-project

# 2. 查看某个会话的详情
uv run sessions.py get sess_abc123
```

### 工作流 2：新任务

```bash
# 执行任务（会话自动保存到 ~/.claude/projects/）
uv run sessions.py exec "分析 E:/my-project 的代码结构" --cwd E:/my-project

# 输出: {"success": true, "session_id": "sess_xxx", ...}
```

### 工作流 3：继续任务

```bash
# 使用上一步的 session_id 继续任务
uv run sessions.py exec "找出所有 TODO 注释" --resume sess_xxx --cwd E:/my-project
```

---

## 错误处理

| 错误 | 处理 |
|------|------|
| SDK 未安装 | 运行 `uv sync` |
| 会话不存在 | 检查 session_id 是否正确 |
| 项目无历史 | 先执行任务创建会话 |
| 权限错误 | 检查工作目录权限 |

---

## 教练关联

- **CEO Coach**: [ceo-coach](../ceo-coach/SKILL.md) - 任务分配与验收
- **opc-ceo-core**: [opc-ceo-core](../opc-ceo-core/SKILL.md) - 被调用的 CEO 技能
