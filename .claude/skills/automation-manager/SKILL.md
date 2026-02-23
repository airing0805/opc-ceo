---
name: automation-manager
description: 工作流自动化与定时任务
version: 1.0.0
source: local-creation
author: OPC-CEO
modules:
  - 工作流定义
  - 触发器
  - 执行器
---

# 自动化专家

## 角色定位

负责工作流自动化与定时任务的定义、配置和执行。

## 核心能力

- 定时任务定义（Cron 表达式）
- 工作流设计（顺序、并行、条件）
- 触发器配置（时间、事件）
- 任务执行（调用其他技能）
- 执行日志

## 默认配置

| 配置项 | 值 |
|--------|-----|
| 工作流 ID 格式 | `WF-YYYY-MM-DD-NNN` |
| 时区 | `Asia/Shanghai` |
| Cron 格式 | 标准 5 段格式 |
| 重试次数 | 3 |

## 模块索引

| 模块 | 说明 |
|------|------|
| 工作流定义 | 工作流格式、步骤定义、变量传递 |
| 触发器 | 定时触发、事件触发配置 |
| 执行器 | 执行逻辑、错误重试、日志记录 |

## 与 scheduler skill 的集成

automation-manager 通过 scheduler skill 实现定时任务：
- 定义工作流
- 配置触发器
- 调用其他技能执行具体任务

## 工作流数据模型

### 工作流实体 (Workflow)

| 属性 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `workflowId` | string | 是 | 工作流 ID，格式 `WF-YYYY-MM-DD-NNN` |
| `name` | string | 是 | 工作流名称 |
| `description` | string | 否 | 工作流描述 |
| `trigger` | object | 是 | 触发器配置 |
| `steps` | array | 是 | 工作流步骤 |
| `variables` | object | 否 | 变量定义 |
| `status` | string | 是 | 状态：`active` / `paused` / `disabled` |
| `createdAt` | string | 是 | 创建时间 |
| `updatedAt` | string | 是 | 更新时间 |

## 使用示例

### 示例 1：每日回顾工作流

```yaml
workflow:
  id: WF-2026-02-24-001
  name: 每日回顾
  trigger:
    type: cron
    schedule: "0 18 * * *"  # 每天 18:00
  steps:
    - name: 收集完成的任务
      skill: task-manager
      action: get-completed-today
    - name: 生成日报
      skill: task-manager
      action: generate-daily-report
    - name: 保存报告
      skill: file-manager
      action: save-file
```

### 示例 2：周报告工作流

```yaml
workflow:
  id: WF-2026-02-24-002
  name: 周报生成
  trigger:
    type: cron
    schedule: "0 18 * * 5"  # 每周五 18:00
  steps:
    - name: 汇总本周任务
      skill: task-manager
      action: get-weekly-summary
    - name: 分析时间分配
      skill: schedule-manager
      action: analyze-weekly-time
    - name: 生成周报
      action: generate-report
    - name: 发送报告
      skill: file-manager
      action: save-file
```

### 示例 3：事件触发工作流

```yaml
workflow:
  id: WF-2026-02-24-003
  name: 任务完成后提醒
  trigger:
    type: event
    eventType: task-completed
  steps:
    - name: 记录完成时间
      skill: schedule-manager
      action: log-completion-time
    - name: 更新状态
      skill: task-manager
      action: update-status
```

## 工作流类型

### 顺序工作流

步骤按顺序执行，前一个步骤完成后执行下一个。

### 并行工作流

多个步骤同时执行，全部完成后进入下一步。

### 条件工作流

根据条件决定执行哪个步骤。

## 数据存储

所有工作流数据存储在 MCP Memory 知识图谱中：
- `Workflow` 实体：工作流定义
- `WorkflowExecution` 实体：执行记录

## 能力边界

**能做**：
- 工作流定义和管理
- 触发器配置
- 调用其他技能执行任务
- 执行日志记录

**不能做**：
- 文件系统操作（由 file-manager 负责）
- 任务管理（由 task-manager 负责）
- 日程管理（由 schedule-manager 负责）

## 教练关联

- **Automation Coach**: [教练-automation-manager](../教练-automation-manager/SKILL.md) - 负责评估和指导自动化能力

## 注意事项

- 工作流步骤必须明确技能和操作
- 触发器配置需要验证有效性
- 执行失败需要记录日志
- 重试机制要防止无限循环
