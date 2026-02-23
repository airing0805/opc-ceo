# Claude SDK 执行器 (claude-sdk-executor)

## 角色定位

通过 Claude API/SDK 进行程序化调用的执行层

## 能力要求

- Claude API 调用（Messages API、Tools）
- 批量处理任务
- 自动化工作流执行
- 其他 skills 的程序化调用
- 结果解析与存储

## 技术栈

- Anthropic Python SDK (`anthropic`)
- 或通过 Bash 调用 `claude` CLI

## 技能文件

| 文件 | 职责 |
|------|------|
| `SKILL.md` | 主入口 - SDK 配置、认证、调用模式 |
| `API调用.md` | Messages API 调用模式、工具使用 |
| `批量处理.md` | 批量任务处理、并发控制 |
| `技能调用.md` | 程序化调用其他 skills |
| `结果处理.md` | 结果解析、存储、错误处理 |

## 调用模式

### 模式 1：Bash 调用 Claude CLI

```bash
# 单次对话
claude -p "你的提示"

# 带文件上下文
claude -p "分析这个文件" -f input.txt

# 使用特定模型
claude -p "任务" --model claude-sonnet-4-20250514
```

### 模式 2：通过 MCP 工具

- 使用现有的 Task 工具启动 agent
- 调用 Skill 工具执行技能

## 架构图

```
┌─────────────────────────────────────────────────────────┐
│              claude-sdk-executor                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌────────────┐  │
│  │ API Calls   │    │ Batch       │    │ Skill      │  │
│  │ Messages    │    │ Processing  │    │ Invocation │  │
│  │ Tools       │    │ Concurrent  │    │ Programmatic│ │
│  └──────┬──────┘    └──────┬──────┘    └─────┬──────┘  │
│         │                  │                  │         │
│         └──────────────────┼──────────────────┘         │
│                            │                            │
│                   ┌────────▼────────┐                   │
│                   │ Result Handler  │                   │
│                   │ Parse/Store     │                   │
│                   └─────────────────┘                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 教练角色

参见：[教练-claude-sdk-executor](./教练-08-claude-sdk-executor.md)
