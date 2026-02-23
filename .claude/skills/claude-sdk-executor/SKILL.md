---
name: claude-sdk-executor
description: 通过 Claude API/SDK 进行程序化调用的执行层
version: 1.0.0
source: local-creation
author: OPC-CEO
modules:
  - API调用
  - 批量处理
  - 技能调用
  - 结果处理
---

# Claude SDK 执行器

## 角色定位

通过 Claude API/SDK 进行程序化调用的执行层，负责 API 调用、批量处理、技能调用和结果处理。

## 核心能力

- Claude API 调用（Messages API、Tools）
- 批量处理任务（并发控制、任务队列）
- 自动化工作流执行
- 其他 skills 的程序化调用
- 结果解析与存储

## 默认配置

| 配置项 | 值 |
|--------|-----|
| API Key | 环境变量 `ANTHROPIC_API_KEY` |
| 模型 | 默认 `claude-sonnet-4-20250514` |
| 超时 | 180 秒 |
| 最大并发 | 3 |

## 模块索引

| 模块 | 文件 | 说明 |
|------|------|------|
| API调用 | [API调用.md](API调用.md) | Messages API 调用模式、工具使用 |
| 批量处理 | [批量处理.md](批量处理.md) | 批量任务处理、并发控制 |
| 技能调用 | [技能调用.md](技能调用.md) | 程序化调用其他 skills |
| 结果处理 | [结果处理.md](结果处理.md) | 结果解析、存储、错误处理 |

## 技术栈

| 方式 | 说明 |
|------|------|
| Anthropic Python SDK | `anthropic` 包 |
| Bash 调用 Claude CLI | `claude` 命令 |
| MCP Task 工具 | 启动 agent 并执行 |
| MCP Skill 工具 | 调用技能 |

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

```
使用 Task 工具启动 agent
使用 Skill 工具调用技能
```

## 使用示例

### 示例 1：单次 API 调用

```
用户: "用 Claude 分析这个文件"

claude-sdk-executor 处理:
1. 使用 Bash 调用 claude CLI
2. 传递文件内容和提示
3. 返回解析后的结果
```

### 示例 2：批量处理

```
用户: "批量分析这 10 个文件"

claude-sdk-executor 处理:
1. 创建 10 个并发任务
2. 限制最大并发为 3
3. 按队列执行并收集结果
4. 返回汇总报告
```

### 示例 3：技能调用

```
用户: "调用 task-manager 创建任务"

claude-sdk-executor 处理:
1. 使用 Skill 工具调用 task-manager
2. 传递任务参数
3. 返回任务 ID
```

## 最佳实践

1. **错误处理** - 捕获并记录所有 API 错误
2. **结果解析** - 从 API 响应中提取关键信息
3. **结果存储** - 重要结果存储到知识图谱
4. **并发控制** - 限制并发数避免超限
5. **超时处理** - 设置合理的超时时间

## 注意事项

- API Key 通过环境变量配置，不要硬编码
- 敏感信息不要记录到日志
- 调用失败要重试机制
- 结果要验证完整性

## 能力边界

| 可以做 | 不能做 |
|--------|--------|
| API/SDK 调用 | 业务决策 |
| 批量处理 | 用户交互 |
| 技能调用 | 跨角色协调 |

## Coach-CEO 沟通桥接

### 架构角色

`claude-sdk-executor` 是 Coach 和 CEO 之间的通信桥梁，负责：

1. **接收 Coach 请求** - 解析评估/指导/检查任务
2. **上下文管理** - 从 MCP Memory 读取历史数据
3. **会话决策** - 判断是否需要新会话
4. **执行 CEO 技能** - 调用 opc-ceo-core
5. **结果验证** - 验证任务完成度
6. **返回结构化结果** - 按 Coach 要求格式返回

### 处理流程

```
┌─────────────────────────────────────────────────────────────────┐
│              Coach-CEO 沟通桥接处理流程                       │
└─────────────────────────────────────────────────────────────────┘

1. 接收请求
   ├─ taskType: 评估|指导|检查
   ├─ taskId: TASK-YYYY-MM-DD-NNN
   └─ evaluationStandards: {...}

2. 上下文检查
   ├─ 读取 MCP Memory 中的历史数据
   ├─ 验证必需上下文是否完整
   └─ 如缺失，标记 contextNeeded

3. 会话决策
   ├─ 任务复杂度 >= 高 → 创建新会话
   ├─ 需要深度推理 → 创建新会话
   ├─ 评估周期任务 → 创建新会话
   └─ 简单查询 → 同一会话执行

4. 执行 CEO 技能
   ├─ 使用 Skill 工具调用 opc-ceo-core
   ├─ 传递任务参数和上下文
   └─ 等待 CEO 执行结果

5. 结果验证
   ├─ 检查输出完整性
   ├─ 验证决策明确性
   ├─ 确认行动清单
   └─ 评估置信度

6. 返回结果
   └─ 返回结构化 JSON 给 Coach
```

### 上下文管理规则

| 场景 | 上下文来源 |
|------|-----------|
| **周期评估** | 从 MCP Memory 读取 `Decision`, `Context` 实体 |
| **历史查询** | 从 MCP Memory 读取 `RoleCapability` 实体 |
| **角色检查** | 从 MCP Memory 读取各角色最新状态 |

### 会话决策矩阵

| 任务类型 | 复杂度 | 新会话 | 上下文传递 |
|---------|--------|--------|-----------|
| 周期评估 | 高 | ✅ | MCP Memory |
| 成长指导 | 高 | ✅ | MCP Memory |
| 简单查询 | 低 | ❌ | 直接传递 |
| 单项检查 | 中 | ❌ | 直接传递 |

### 执行示例

#### 示例 1：周期评估（创建新会话）

```bash
# 1. 从 MCP Memory 读取本周数据
mcp__memory__search_nodes: "eval-opc-ceo-core-2026-02-23"

# 2. 创建新会话执行 CEO 技能
# 通过 Skill 工具调用 opc-ceo-core

# 3. 返回结构化结果
{
  "taskId": "TASK-2026-02-23-001",
  "status": "completed",
  "confidence": 0.95,
  "result": { /* CEO 评估结果 */ },
  "actionItems": [],
  "contextNeeded": [],
  "newSessionRecommended": true
}
```

#### 示例 2：简单查询（同一会话）

```bash
# 1. 直接调用 CEO 技能
Skill: opc-ceo-core

# 2. 返回结果
{
  "taskId": "TASK-2026-02-23-002",
  "status": "completed",
  "confidence": 0.90,
  "result": { /* CEO 查询结果 */ },
  "actionItems": [],
  "contextNeeded": [],
  "newSessionRecommended": false
}
```

### 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| **上下文缺失** | 返回 `status: partial`, 标记 `contextNeeded` |
| **CEO 执行失败** | 返回 `status: failed`, 记录错误详情 |
| **结果不完整** | 返回 `status: partial`, 标记缺失字段 |
| **置信度过低** | 返回 `status: partial`, 建议 `newSessionRecommended: true` |

## 教练关联

- **CEO Coach**: [ceo-coach](../ceo-coach/SKILL.md) - 任务分配与验收
- **opc-ceo-core**: [opc-ceo-core](../opc-ceo-core/SKILL.md) - 被调用的 CEO 技能
- **Executor Coach**: [教练-claude-sdk-executor](../../plans/v1-技能规划/角色设计/教练-08-claude-sdk-executor.md) - 技能优化指导
