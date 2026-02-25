# Claude SDK 执行器 (claude-sdk-executor)

> **注意**：此文档属于 V1 版本规划，已于 2026-02-24 废弃。
>
> V1 基于纯 Skills 架构，V2 已转向原生 Team/SendMessage API 协作架构。
>
> 当前版本请参考：[V2 规划总览](../../v2-技能规划/README.md)
>
> 原有 Skills 已归档至：`.claude/skills/disabled/`
>
> **注意**：claude-sdk-executor 在 V2 中仍然保留，作为程序化执行的工具。

---

## 角色定位

**独立会话执行层** - 通过 Bash 执行 Python 脚本，使用 `claude-agent-sdk` 调用 Claude Code API，实现完全独立的会话执行。

**核心价值**：
- 解决嵌套会话导致的上下文层级过深问题
- 提供 session_id 用于任务追踪和会话续传
- 支持批量处理和自动化工作流
- **利用 Claude Code 原生会话管理** - 会话历史自动保存到 `~/.claude/`

## 能力要求

### 基础能力

| 能力 | 标准 |
|------|------|
| **请求构造** | 构造执行请求参数（prompt, session_id, cwd, tools 等） |
| **脚本执行** | 通过 Bash 执行 `uv run sessions.py exec <prompt>` |
| **SDK 调用** | 使用 `claude-agent-sdk.ClaudeAgentClient` 执行任务 |
| **结果解析** | 解析返回的 session_id, result, turns, cost_usd |
| **错误处理** | 处理 SDK 错误、网络异常、脚本执行失败 |

### 扩展能力

| 能力 | 标准 |
|------|------|
| **批量处理** | 支持并发执行多个独立会话 |
| **工作流编排** | 支持多步骤自动化任务 |
| **会话关联** | 通过 session_id 追踪和管理多个独立会话 |
| **多轮对话** | 通过 resume 参数维护会话上下文 |

## 核心职责

### 1. 独立会话执行

```
输入 → 构造请求 → Bash 执行脚本 → SDK 调用 → 解析结果 → 输出
```

**执行流程**：

| 步骤 | 说明 |
|------|------|
| 1. 构造请求 | 生成执行参数（prompt, session_id, cwd, tools） |
| 2. 执行脚本 | `uv run sessions.py exec "<prompt>" --resume <session_id> --cwd <path>` |
| 3. 调用 SDK | `ClaudeAgentClient` 发起任务 |
| 4. 解析结果 | 提取 session_id, result, turns, cost_usd |
| 5. 输出结果 | JSON 格式返回 |

### 2. 会话管理

| 操作 | 命令 | 说明 |
|------|------|------|
| **列出会话** | `uv run sessions.py list --cwd <path>` | 列出项目的历史会话 |
| **获取详情** | `uv run sessions.py get <session_id>` | 获取指定会话的详细信息 |
| **删除会话** | `uv run sessions.py delete <session_id>` | 删除指定会话 |

### 3. 多轮对话支持

- **首次执行**：不传 `--resume`，创建新会话，返回新的 `session_id`
- **继续对话**：传入 `--resume <session_id>`，恢复会话上下文
- **会话存储**：自动保存到 `~/.claude/projects/<project_hash>/<session_id>.jsonl`

### 4. 会话追踪

- 每次执行返回 `session_id` 用于标识会话
- 支持通过 `session_id` 恢复对话
- 支持查询会话历史和详情

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
│  │ Bash: uv run sessions.py exec "分析项目" --cwd .      │  │
│  │  ↓                                                   │  │
│  │ ClaudeAgentClient 创建新会话                            │  │
│  │  ↓                                                   │  │
│  │ 返回: { session_id, result, turns, cost_usd }         │  │
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
│  │ 返回: { session_id, result, turns, cost_usd }         │  │
│  └─────────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
                    ... (可继续多轮)
```

## 会话存储机制

### 存储位置

```
~/.claude/projects/<project_hash>/<session_id>.jsonl
```

- `project_hash`：项目路径的 MD5 哈希（前 16 位）
- `session_id`：Claude Code 生成的会话标识
- `.jsonl`：JSON Lines 格式，每行一条消息

### 会话元数据

```json
{
  "session_id": "abc123-def456",
  "title": "分析项目代码结构",
  "timestamp": "2026-02-24T10:00:00Z",
  "message_count": 15,
  "cwd": "E:/workspaces/OPC-CEO"
}
```

## 请求格式

### 执行请求（新建会话）

```bash
uv run sessions.py exec "<prompt>" --cwd <path>
```

### 执行请求（续传会话）

```bash
uv run sessions.py exec "<prompt>" --resume <session_id> --cwd <path>
```

### 输出格式（JSON）

```json
{
  "success": true,
  "session_id": "abc123-def456",
  "result": "执行结果内容",
  "turns": 3,
  "cost_usd": 0.0125
}
```

### 错误格式

```json
{
  "success": false,
  "error": "错误类型",
  "session_id": null
}
```

## 技术栈

| 组件 | 说明 |
|------|------|
| **Python** | 脚本执行引擎 |
| **claude-agent-sdk** | Claude Code 官方 SDK |
| **Bash** | 执行入口 |
| **uv** | Python 包管理和执行 |
| **JSONL** | 会话存储格式 |

## 执行流程图（完整版）

```
┌─────────────────────────────────────────────────────────────────┐
│                     CEO Agent (主会话)                         │
│  协调各专业角色，识别需要独立执行的任务                        │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ 1. 构造执行参数
                     │    - prompt: 任务描述
                     │    - session_id: (可选) 续传会话
                     │    - cwd: 工作目录
                     │    - tools: 允许的工具
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              Bash Tool: uv run sessions.py exec                │
│  执行 Python 脚本，传入命令行参数                             │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                sessions.py (Python 脚本)                      │
│  ---------------------------------------------------------    │
│  1. 解析命令行参数                                           │
│  2. 创建 ClaudeAgentOptions (含 resume 参数)                    │
│  3. 创建 ClaudeAgentClient                                    │
│  4. 发起任务查询 (client.query(prompt))                        │
│  5. 接收响应流 (client.receive_response())                    │
│  6. 提取结果 (result, session_id, turns, cost_usd)            │
│  7. 输出 JSON 到 stdout                                      │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              claude-agent-sdk (SDK 层)                        │
│  ---------------------------------------------------------    │
│  1. 调用 Claude Code API                                     │
│  2. 管理会话上下文（resume 时自动加载历史）                     │
│  3. 返回消息流                                                │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ Claude Code 自动保存会话
                     │ 到 ~/.claude/projects/
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CEO Agent (主会话)                         │
│  解析返回结果，继续后续协调工作                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 命令参考

### 列出会话

```bash
uv run sessions.py list --cwd <path>
```

**输出**：
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

### 执行任务

```bash
# 新建会话
uv run sessions.py exec "分析这个项目" --cwd .

# 续传会话
uv run sessions.py exec "继续分析" --resume abc123-def456 --cwd .

# 指定允许的工具
uv run sessions.py exec "只使用 Read 工具" --tools Read --cwd .
```

### 其他命令

```bash
# 获取会话详情
uv run sessions.py get <session_id>

# 删除会话
uv run sessions.py delete <session_id>

# 列出所有项目
uv run sessions.py projects
```

## 文件结构

```
.claude/skills/claude-sdk-executor/
├── SKILL.md                 # 主入口（本文档）
└── scripts/
    ├── sessions.py          # 会话管理和执行脚本
    ├── pyproject.toml       # Python 项目配置
    ├── .venv/              # 虚拟环境
    └── uv.lock             # 依赖锁文件
```

## 能力边界

| 能做 | 不能做 |
|------|--------|
| 执行独立会话 | 直接操作 Claude Code CLI |
| 多轮对话（通过 resume） | 业务决策（交给 CEO） |
| 批量处理 | 用户交互（交给 CEO） |
| 会话查询和追踪 | - |

## 使用场景

| 场景 | 说明 |
|------|------|
| **批量分析** | 需要独立处理多个相似任务 |
| **深度推理** | 需要干净上下文的任务 |
| **自动化流程** | 定时任务中的独立调用 |
| **复杂计算** | 需要独立资源占用的任务 |
| **多轮交互** | 需要持续上下文的对话式任务 |

