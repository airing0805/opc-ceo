# API调用

## 功能概述

定义 Claude Messages API 的调用模式和工具使用。

## 操作命令

### 命令 1：单次调用

**用途**：发起单次 Claude API 调用

**语法**：
```
单次调用:
  - prompt: <提示词>
  - model: <模型> (可选)
  - maxTokens: <最大Token数> (可选)
  - system: <系统提示> (可选)
```

**参数**：

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| prompt | string | 是 | 提示词 |
| model | string | 否 | 模型名称 |
| maxTokens | number | 否 | 最大 Token 数 |
| system | string | 否 | 系统提示 |
| tools | array | 否 | 工具定义 |

**示例**：
```
单次调用:
  - prompt: "分析以下代码并给出优化建议"
  - model: claude-sonnet-4-20250514
  - maxTokens: 4096
```

---

### 命令 2：带上下文调用

**用途**：携带文件或其他上下文的调用

**语法**：
```
带上下文调用:
  - prompt: <提示词>
  - contextFiles: <上下文文件> (可选)
  - system: <系统提示> (可选)
```

**参数**：

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| prompt | string | 是 | 提示词 |
| contextFiles | array | 否 | 上下文文件路径列表 |
| system | string | 否 | 系统提示 |

**示例**：
```
带上下文调用:
  - prompt: "分析文件内容"
  - contextFiles: ["E:\\Documents\\设计文档.md"]
```

---

### 命令 3：工具调用

**用途**：定义并使用 API 工具

**语法**：
```
工具调用:
  - prompt: <提示词>
  - tools: <工具列表>
```

**工具格式**：

```json
{
  "name": "工具名称",
  "description": "工具描述",
  "input_schema": {
    "type": "object",
    "properties": {
      "参数名": {
        "type": "参数类型",
        "description": "参数描述"
      }
    },
    "required": ["必需参数"]
  }
}
```

**示例**：

```json
{
  "name": "create_task",
  "description": "创建新任务",
  "input_schema": {
    "type": "object",
    "properties": {
      "title": {"type": "string", "description": "任务标题"},
      "priority": {"type": "string", "description": "优先级"}
    },
    "required": ["title"]
  }
}
```

---

## Bash 调用方式

### 单次对话

```bash
claude -p "你的提示"
```

### 带文件上下文

```bash
claude -p "分析这个文件" -f input.txt
```

### 使用特定模型

```bash
claude -p "任务" --model claude-sonnet-4-20250514
```

### 使用环境变量

```bash
export ANTHROPIC_API_KEY=sk-xxx
claude -p "提示"
```

---

## 响应解析

### Messages API 响应格式

```json
{
  "id": "msg_xxx",
  "type": "message",
  "role": "assistant",
  "content": [
    {"type": "text", "text": "响应内容"}
  ],
  "model": "claude-sonnet-4-20250514",
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 123,
    "output_tokens": 456
  }
}
```

### 工具调用响应格式

```json
{
  "id": "msg_xxx",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "tool_use",
      "id": "toolu_xxx",
      "name": "工具名称",
      "input": {"参数": "值"},
      "use_tool_stop": true
    }
  ],
  "stop_reason": "tool_use"
}
```

---

## 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| API 错误 | 记录错误，返回友好的错误信息 |
| 超时 | 设置合理超时，记录超时事件 |
| 认证失败 | 检查 API Key 配置 |
| 速率限制 | 添加延迟重试机制 |

---

## 相关模块

- [批量处理](批量处理.md) - 批量任务处理
- [技能调用](技能调用.md) - 程序化调用 skills
- [结果处理](结果处理.md) - 结果解析、存储
