# Claude SDK Executor

通过 Bash 执行 Python 脚本，使用 `claude-agent-sdk` 调用 Claude Code API，实现完全独立的会话执行。

## 核心价值

- 解决嵌套会话导致的上下文层级过深问题
- 提供 `session_id` 用于任务追踪和会话续传
- 支持批量处理和自动化工作流
- 利用 Claude Code 原生会话管理 - 会话历史自动保存到 `~/.claude/`

## 安装

```bash
# 克隆项目
git clone <repository-url>
cd OPC-CEO

# 安装依赖
uv sync
```

## 使用

### 列出项目会话

```bash
uv run claude-executor list --cwd <path>
```

### 列出所有项目

```bash
uv run claude-executor projects
```

### 获取会话详情

```bash
uv run claude-executor get <session_id>
```

### 删除会话

```bash
uv run claude-executor delete <session_id>
```

### 执行任务（新建会话）

```bash
uv run claude-executor exec "<prompt>" --cwd <path>
```

### 续传会话（多轮对话）

```bash
uv run claude-executor exec "<prompt>" --resume <session_id> --cwd <path>
```

## 命令参数

| 参数 | 说明 |
|------|------|
| `--cwd <path>` | 工作目录 |
| `--resume <session_id>` | 恢复指定会话 |
| `--tools <tool1,tool2>` | 允许的工具列表（默认：Read,Glob,Grep,Bash） |

## 输出格式

### 成功响应

```json
{
  "success": true,
  "session_id": "abc123-def456",
  "result": "执行结果内容",
  "turns": 3,
  "cost_usd": 0.0125
}
```

### 错误响应

```json
{
  "success": false,
  "error": "错误类型",
  "session_id": null
}
```

## 会话存储

会话自动保存到：
```
~/.claude/projects/<project_hash>/<session_id>.jsonl
```

- `project_hash`：项目路径的路径替换格式
- `session_id`：Claude Code 生成的会话标识
- `.jsonl`：JSON Lines 格式，每行一条消息

## 开发

### 运行测试

```bash
uv run pytest
```

### 测试覆盖率

```bash
uv run pytest --cov=src/claude_sdk_executor --cov-report=html
```

## 项目结构

```
src/claude_sdk_executor/
├── __init__.py       # 包初始化
├── sessions.py        # 会话管理核心逻辑
├── cli.py            # CLI 入口
└── exceptions.py      # 自定义异常

tests/
├── __init__.py
└── test_sessions.py   # 单元测试
```

## 许可证

MIT
