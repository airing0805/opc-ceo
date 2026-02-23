---
name: claude-sdk-executor
description: 通过 Bash 执行 Python 脚本，使用 claude-agent-sdk 调用 Claude Code API，实现独立会话执行
---

# Claude SDK 执行器

## 角色定位

**独立会话执行层** - 通过 Bash 执行 Python 脚本，使用 `claude-agent-sdk` 调用 Claude Code API，实现完全独立的会话执行。

**核心价值**：
- 解决嵌套会话导致的上下文层级过深问题
- 提供 `session_id` 用于任务追踪和会话续传
- 支持批量处理和自动化工作流
- **利用 Claude Code 原生会话管理** - 会话历史自动保存到 `~/.claude/`

**重要说明**：
- `claude-agent-sdk` 会检测当前是否在 Claude Code 会话中运行（通过 `CLAUDECODE` 环境变量）
- 在当前 Claude Code 会话中调用 SDK 会被拒绝，防止嵌套资源冲突
- **主要使用场景**：自动化流程（如 `schedule-manager`）、定时任务、独立进程调用
- **不建议在当前会话中交互式调用**，因为会被 SDK 的嵌套检测阻止

**唤醒响应规范**：当用户唤醒 claude-sdk-executor 时，第一次回答必须以"我是 claude-sdk-executor"开头。

## 触发场景

当用户提出以下类型的请求时触发：

| 用户请求 | 示例 |
|----------|------|
| 要求 claude 做某事 | "claude，帮我分析这个项目" |
| 要求 claude 执行任务 | "claude，写一个脚本" |
| 要求 claude 处理文件 | "claude，整理这些代码" |
| 要求 claude 运行命令 | "claude，执行测试" |
| 要求 claude 调研分析 | "claude，研究某个技术" |
| 要求 claude 编写代码 | "claude，实现某个功能" |

## 核心能力

- **独立会话执行** - 通过 Bash 执行 Python 脚本，使用 claude-agent-sdk 调用 Claude Code API
- **多轮对话支持** - 通过 `--resume <session_id>` 恢复会话上下文
- **会话管理** - 列出、删除、查看 Claude Code 历史会话详情
- **项目管理** - 查看所有有历史记录的项目

## 架构设计

### 执行原理

通过 **Bash 执行 Python 脚本**，脚本中使用 `claude-agent-sdk.ClaudeAgentClient` 调用 Claude Code API：

```python
# Python 脚本（在独立进程中执行）
from claude_agent_sdk import ClaudeAgentOptions, ClaudeAgentClient
import asyncio

async def execute():
    options = ClaudeAgentOptions(
        permission_mode="acceptEdits",
        cwd=".",
    )
    async with ClaudeAgentClient(options=options) as client:
        await client.query("分析项目")
        async for message in client.receive_response():
            # 处理响应...
            pass

asyncio.run(execute())
```

```bash
# 通过 Bash 执行 Python 脚本（独立进程）
uv run sessions.py exec "分析项目" --cwd .
```

**关键设计**：
- Bash 执行会创建**新的 Python 进程**
- 独立进程中的 SDK 调用形成**独立的 Claude 会话**
- 绕过当前 Claude 会话的嵌套限制

### 执行流程

```
用户请求（当前 Claude 会话）
   │
   ▼
claude-sdk-executor 接收
   │
   ▼
构造执行参数（prompt, session_id, cwd, tools）
   │
   ▼
通过 Bash 执行: uv run sessions.py exec
   │
   ├─▶ 产生独立的 Python 进程
   │
   ▼
新进程调用 claude-agent-sdk
   │
   ├─▶ ClaudeAgentClient.query(prompt)
   │  └─▶ 接收消息流 receive_response()
   │
   ├─▶ 创建新的 Claude 会话（无嵌套限制）
   │
   ▼
Claude Code API 处理请求并返回
   │
   │ Claude Code 自动保存会话
   │ 到 ~/.claude/projects/
   │
   ▼
通过 Bash 捕获输出（JSON 格式）
   │
   ▼
返回结果给用户（在当前会话中）
```

### 会话存储机制

会话自动保存到：
```
~/.claude/projects/<project_hash>/<session_id>.jsonl
```

- `project_hash`：项目路径的 MD5 哈希（前 16 位）
- `session_id`：Claude Code 生成的会话标识
- `.jsonl`：JSON Lines 格式，每行一条消息

## 依赖安装

```bash
cd .claude/skills/claude-sdk-executor/scripts
uv sync
```

## 操作命令

### 命令 1：列出项目会话

**用途**：查看指定项目的历史会话

**语法**：
```bash
uv run sessions.py list --cwd <path>
```

**参数**：

| 参数 | 说明 |
|------|------|
| `--cwd <path>` | 项目目录（必需） |

**示例**：

```bash
# 列出项目的历史会话
uv run sessions.py list --cwd E:/workspaces/OPC-CEO
```

**输出示例**：
```json
{
  "sessions": [
    {
      "id": "abc123-def456",
      "title": "分析项目代码结构",
      "timestamp": "2026-02-24T10:00:00Z",
      "message_count": 15,
      "size": 8192,
      "tools": ["Read", "Glob", "Grep"],
      "cwd": "E:/workspaces/OPC-CEO"
    }
  ],
  "count": 1,
  "cwd": "."
}
```

---

### 命令 2：列出所有项目

**用途**：查看所有有历史记录的项目

**语法**：
```bash
uv run sessions.py projects
```

**输出示例**：
```json
{
  "projects": [
    {
      "hash": "e8f4a1b2c3d4e5f6",
      "path": "E:/workspaces/OPC-CEO",
      "session_count": 5
    }
  ],
  "count": 1
}
```

---

### 命令 3：获取会话详情

**用途**：查看指定会话的详细信息

**语法**：
```bash
uv run sessions.py get <session_id>
```

**输出示例**：
```json
{
  "id": "abc123-def456",
  "title": "分析项目代码结构",
  "timestamp": "2026-02-24T10:00:00Z",
  "message_count": 15,
  "size": 8192,
  "tools": ["Read", "Glob", "Grep"],
  "cwd": "E:/workspaces/OPC-CEO",
  "file_path": "C:/Users/Administrator/.claude/projects/e8f4a1b2c3d4e5f6/abc123-def456.jsonl"
}
```

---

### 命令 4：删除会话

**用途**：删除会话历史文件

**语法**：
```bash
uv run sessions.py delete <session_id>
```

**输出示例**：
```json
{
  "deleted": true
}
```

---

### 命令 5：执行任务（新建会话）

**用途**：通过 Bash 执行 Python 脚本，创建独立 Claude 会话并执行任务

**语法**：
```bash
uv run sessions.py exec "<prompt>" --cwd <path>
```

**参数**：

| 参数 | 说明 |
|------|------|
| `<prompt>` | 任务提示（必需） |
| `--cwd <path>` | 工作目录 |
| `--tools <tool1,tool2>` | 允许使用的工具列表（默认：Read,Glob,Grep,Bash） |

**示例**：

```bash
# 创建独立会话执行任务
uv run sessions.py exec "分析这个项目的结构" --cwd E:/workspaces/OPC-CEO

# 指定允许的工具
uv run sessions.py exec "只使用 Read 工具分析文件" --tools Read --cwd .
```

**输出示例**：
```json
{
  "success": true,
  "session_id": "abc123-def456",
  "result": "项目目录结构如下...",
  "turns": 3,
  "cost_usd": 0.0125
}
```

**错误输出示例**：
```json
{
  "success": false,
  "error": "错误类型",
  "session_id": null
}
```

---

### 命令 6：续传会话（多轮对话）

**用途**：恢复已有的会话上下文，继续多轮对话

**语法**：
```bash
uv run sessions.py exec "<prompt>" --resume <session_id> --cwd <path>
```

**参数**：

| 参数 | 说明 |
|------|------|
| `<prompt>` | 任务提示（必需） |
| `--resume <session_id>` | 要恢复的会话 ID（必需） |
| `--cwd <path>` | 工作目录 |

**示例**：

```bash
# 继续之前的对话
uv run sessions.py exec "继续分析" --resume abc123-def456 --cwd E:/workspaces/OPC-CEO

# 基于之前的结果进行进一步分析
uv run sessions.py exec "根据刚才的分析结果，总结关键问题" --resume abc123-def456 --cwd .
```

---

## 多轮对话流程

```
┌─────────────────────────────────────────────────────────────────┐
│                     CEO Agent (主会话)                         │
│  协调各专业角色，识别需要执行的任务                            │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              第一轮对话：新建会话                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Bash: uv run sessions.py exec "分析项目" --cwd .   │  │
│  │  ↓                                                   │  │
│  │ ClaudeAgentClient 创建新会话                            │  │
│  │  ↓                                                   │  │
│  │ 返回: { session_id, result, turns, cost_usd }        │  │
│  └─────────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ session_id: "abc123-def456"
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CEO Agent (主会话)                         │
│  用户继续提问，传入 session_id                                │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              第二轮对话：续传会话                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Bash: uv run sessions.py exec "继续分析..."          │  │
│  │       --resume abc123-def456 --cwd .                  │  │
│  │  ↓                                                   │  │
│  │ ClaudeAgentClient 恢复会话（加载历史）                  │  │
│  │  ↓                                                   │  │
│  │ 返回: { session_id, result, turns, cost_usd }        │  │
│  └─────────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
                    ... (可继续多轮)
```

## 典型工作流

### 工作流 1：执行任务（新建会话）

```bash
cd .claude/skills/claude-sdk-executor/scripts

# 创建独立会话并执行任务
uv run sessions.py exec "分析项目代码结构" --cwd E:/workspaces/OPC-CEO

# 输出: {"success": true, "session_id": "abc123-def456", "result": "...", "turns": 3, "cost_usd": 0.0125}
```

### 工作流 2：多轮对话

```bash
# 第一轮：创建新会话
uv run sessions.py exec "分析项目结构" --cwd .
# 输出: {"success": true, "session_id": "abc123-def456", ...}

# 第二轮：续传会话继续提问
uv run sessions.py exec "找出所有 Python 文件" --resume abc123-def456 --cwd .

# 第三轮：继续基于上下文提问
uv run sessions.py exec "总结发现的文件结构" --resume abc123-def456 --cwd .
```

### 工作流 3：查看历史会话

```bash
# 列出项目的历史会话
uv run sessions.py list --cwd E:/workspaces/OPC-CEO

# 查看某个会话的详情
uv run sessions.py get abc123-def456

# 列出所有项目
uv run sessions.py projects

# 删除会话
uv run sessions.py delete abc123-def456
```

---

## 错误处理

| 错误 | 处理 |
|------|------|
| claude-agent-sdk 未安装 | 返回 `{"success": false, "error": "claude-agent-sdk 未安装，请运行: uv sync"}` |
| SDK 调用失败 | 返回 `{"success": false, "error": "错误详情", "session_id": null}` |
| 嵌套会话检测失败 | 返回 `"Claude Code cannot be launched inside another Claude Code session."` - 这是 SDK 的保护机制，建议在自动化流程中使用 |
| 会话不存在 | get 命令返回 `{"error": "会话不存在"}` |
| 删除失败 | 返回 `{"deleted": false}` |

---

## 能力边界

| 能做 | 不能做 |
|------|--------|
| 执行独立会话 | 直接操作 Claude Code CLI |
| 多轮对话（通过 resume） | 业务决策（交给 CEO） |
| 批量处理 | 用户交互（交给 CEO） |
| 会话查询和追踪 | - |

---

## 使用场景

| 场景 | 说明 |
|------|------|
| **批量分析** | 需要独立处理多个相似任务 |
| **深度推理** | 需要干净上下文的任务 |
| **自动化流程** | 定时任务中的独立调用 |
| **复杂计算** | 需要独立资源占用的任务 |
| **多轮交互** | 需要持续上下文的对话式任务 |

---

## 教练关联

- **CEO Coach**: [ceo-coach](../ceo-coach/SKILL.md) - 任务分配与验收
- **opc-ceo-core**: [opc-ceo-core](../opc-ceo-core/SKILL.md) - 被调用的 CEO 技能

---

## 文件结构

```
.claude/skills/claude-sdk-executor/
├── SKILL.md                 # 主入口（本文档）
└── scripts/
    ├── sessions.py          # 会话管理和执行脚本
    ├── pyproject.toml       # Python 项目配置
    └── .venv/             # 虚拟环境
```
