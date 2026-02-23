---
name: schedule-manager
description: 时间管理与日程安排
version: 1.0.0
source: local-creation
author: OPC-CEO
modules:
  - 事件操作
  - 每日规划
  - 时间块
  - 时间分析
---

# 日程管理专家

## 角色定位

负责个人/公司的时间管理与日程安排。

## 核心能力

- 日程创建（事件、约会、提醒）
- 日程查询（今日、本周、指定日期）
- 时间块管理（专注时间、会议时间）
- 提醒系统
- 时间统计（时间分配分析）

## 默认配置

| 配置项 | 值 |
|--------|-----|
| 事件 ID 格式 | `EVENT-YYYY-MM-DD-NNN` |
| 时区 | `Asia/Shanghai` |
| 时间格式 | `YYYY-MM-DD HH:mm` |
| 提醒默认提前 | 15 分钟 |

## 模块索引

| 模块 | 说明 |
|------|------|
| 事件操作 | 事件创建、查询、更新、删除、提醒 |
| 每日规划 | 每日规划流程、任务映射 |
| 时间块 | 时间块划分策略、类型定义 |
| 时间分析 | 时间分配统计、趋势分析 |

## 时间块类型

| 类型代码 | 名称 | 说明 | 建议时长 |
|---------|------|------|----------|
| `TB-DEEP` | Deep Work | 深度工作、专注编码 | 2-4 小时 |
| `TB-MEET` | Meetings | 会议沟通、讨论 | 1-2 小时 |
| `TB-ADMIN` | Admin | 行政事务、邮件处理 | 0.5-1 小时 |
| `TB-LEARN` | Learning | 学习成长、阅读 | 1-2 小时 |
| `TB-BREAK` | Breaks | 休息放松、运动 | 0.5 小时 |

## 事件数据模型

### 事件实体 (Event)

| 属性 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `eventId` | string | 是 | 事件 ID，格式 `EVENT-YYYY-MM-DD-NNN` |
| `title` | string | 是 | 事件标题 |
| `startTime` | string | 是 | 开始时间，格式 `YYYY-MM-DD HH:mm` |
| `endTime` | string | 是 | 结束时间，格式 `YYYY-MM-DD HH:mm` |
| `type` | string | 是 | 事件类型（event/meeting/task） |
| `timeBlock` | string | 否 | 时间块类型（TB-XXX） |
| `description` | string | 否 | 事件描述 |
| `location` | string | 否 | 事件地点 |
| `reminder` | number | 否 | 提醒提前时间（分钟） |
| `taskId` | string | 否 | 关联任务 ID |
| `status` | string | 是 | 状态：`pending` / `ongoing` / `completed` / `cancelled` |
| `createdAt` | string | 是 | 创建时间 |
| `updatedAt` | string | 是 | 更新时间 |

## 使用示例

### 示例 1：创建事件

```
用户: "明天下午 2 点有个项目会议，持续 2 小时"

schedule-manager 处理:
1. 生成事件 ID: EVENT-2026-02-24-001
2. 设置时间: 2026-02-24 14:00 - 16:00
3. 时间块: TB-MEET
4. 提醒: 15 分钟前
5. 创建 Event 实体
```

### 示例 2：查询今日日程

```
用户: "今天有什么安排？"

schedule-manager 处理:
1. 查询今日 (2026-02-24) 的所有事件
2. 按时间排序
3. 生成日程视图
```

### 示例 3：时间块规划

```
用户: "帮我规划今天的专注时间"

schedule-manager 处理:
1. 查询今日已有事件
2. 识别可用时间段
3. 创建 TB-DEEP 时间块
4. 设置专注时间提醒
```

## 数据存储

所有日程数据存储在 MCP Memory 知识图谱中：
- `Event` 实体：事件记录

## 能力边界

**能做**：
- 事件创建、查询、更新、删除
- 时间块管理
- 提醒设置
- 时间统计分析

**不能做**：
- 文件系统操作（由 file-manager 负责）
- 任务执行（由 task-manager 负责）
- 知识图谱复杂推理（由 knowledge-manager 负责）

## 教练关联

- **Schedule Coach**: [教练-schedule-manager](../教练-schedule-manager/SKILL.md) - 负责评估和指导时间管理能力

## 注意事项

- 事件时间必须有效（开始时间 < 结束时间）
- 时间块不能重叠（特殊会议除外）
- 提醒时间不能超过事件时长
- 取消事件需要记录原因
