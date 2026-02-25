# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

**OPC-CEO** 是一人公司的 CEO Agent 系统，基于 Claude Code Skills/Agents 实现。

## 设计原则

1. **Agent 和 Skill 优先** - 详见 [V2 协作架构](docs/版本规划/v2-技能规划/Team协作架构.md)
2. **MCP Memory 作为数据层** - 所有数据存储在知识图谱中
3. **统一入口，角色分工** - CEO 协调，各专业角色各司其职
4. **无角色时忘状态** - 没有唤醒角色时，忘掉当前项目的状态，不进行任何假设或操作

## 核心架构

```
            CEO (opc-ceo-core) - 决策协调
                    │
    ┌───────────────┼───────────────┐
    │               │               │
task-manager   file-manager   knowledge-manager
    │               │               │
    └───────────────┼───────────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
finance-manager  schedule-manager  automation-manager
                            │
                            ▼
                claude-sdk-executor (程序化执行)
```

## 实体 ID 命名规范

> 参考文档：`docs/沟通文档/文档沟通规范.md`

| 类型 | 格式 | 示例 |
|------|------|------|
| 任务 | `v2.x.y` | `v2.3.1.1` |
| 协调事件 | `COORD-YYYY-MM-DD-NNN` | `COORD-2026-02-24-001` |
| 对话记录 | `CONV-YYYY-MM-DD-NNN` | `CONV-2026-02-24-001` |
| 进化决策 | `EVO-YYYY-MM-DD-NNN` | `EVO-2026-02-25-001` |

> **说明**：任务使用 `v2.x.y` 格式，直接对应版本规划中的任务组标记。

## 默认配置

| 配置项 | 值 |
|--------|-----|
| Git 项目目录 | `E:\repository_git` |
| 文档命名规范 | **使用中文命名** |
| 临时目录 | `tmp/` - 思考古迹，非正式文档 |
| 文档操作 | **使用 MCP 工具** - 当前电脑环境 Direct 编辑/写入有问题，所有文档操作优先使用 `mcp__filesystem__read_file`、`mcp__filesystem__write_file` 等 MCP 工具 |

## 版本更新规范

### 每日版本规划

- **每日更新**：每天创建一个新的版本规划（如 `v2.6.x`）
- **版本命名**：`v{大版本}.{小版本}.{修订版本}` 格式
- **版本号递增规则**：
  - 修订版本（第三位）：每日小优化/文档更新
  - 小版本（第二位）：完成一个完整功能模块
  - 大版本（第一位）：重大架构变更

### 文档行数触发规范

- **触发阈值**：当单个文档超过 **500 行**时
- **触发动作**：
  1. 停止在该文档中添加新内容
  2. 创建新的子文档或拆分文档
  3. 在原文档中添加索引指向新文档
  4. 制定新的规范或扩展现有规范
- **拆分原则**：
  - 按功能模块拆分
  - 保持文档单一职责
  - 新文档需有清晰的职责边界

## Skill 创建规范

创建 Skill 时必须遵循以下命名规则：

| 文件类型 | 命名规则 | 示例 |
|----------|----------|------|
| 主入口 | `SKILL.md`（固定） | `SKILL.md` |
| 功能模块 | **中文命名** | `任务操作.md`、`项目管理.md` |
| 快速参考 | `快速参考.md` | `快速参考.md` |

**禁止使用**英文模块名如 `task-operations.md`，必须使用中文 `任务操作.md`

## 实现状态

### V1 Skills（已废弃并归档）

所有 V1 Skills 已移动到 `.claude/skills/disabled/` 目录，保留参考用途：
- `opc-ceo-core` - CEO 总控
- `task-manager` - 任务管理
- `file-manager` - 文件管理
- `knowledge-manager` - 知识管理
- `finance-manager` - 财务管理
- `schedule-manager` - 日程管理
- `automation-manager` - 自动化
- `wellness-coach` - 心理健康

### V2 Agents（当前版本）

使用原生 Team/SendMessage API 实现：
- ✅ `ceo-coach` - CEO 教练
- ✅ `claude-sdk-executor` - SDK 执行器
- 📋 后续：基于 V2 协作架构实现各专业角色

## 关键文档

### 当前版本（V2）

| 文档 | 用途 |
|------|------|
| [规划体系.md](docs/规划体系.md) | 规划体系总入口 |
| [README.md](docs/版本规划/v2-技能规划/README.md) | V2 Agent 协作系统规划 |
| [Team协作架构.md](docs/版本规划/v2-技能规划/Team协作架构.md) | Team API 协作架构设计 |
| [SendMessage协作.md](docs/版本规划/v2-技能规划/SendMessage协作.md) | SendMessage API 协作模式 |
| [文档沟通规范.md](docs/沟通文档/文档沟通规范.md) | 沟通文档规范和模板 |
| [公司愿景.md](docs/战略规划/公司愿景.md) | 长期愿景和使命 |
| [战略目标.md](docs/战略规划/战略目标.md) | 年度/季度战略目标 |

### 历史归档（V1）

| 文档 | 用途 |
|------|------|
| [README.md](docs/版本规划/v1-技能规划/README.md) | V1 技能规划总索引 |
| [设计意图.md](docs/版本规划/v1-技能规划/设计意图.md) | V1 版本设计原则、技术决策依据 |
| [模板规范.md](docs/版本规划/v1-技能规划/模板规范.md) | V1 Skill 格式、实体定义、命名规范 |
| [角色设计](docs/版本规划/v1-技能规划/角色设计/) | 各技能的详细设计 |
| [总览.md](docs/版本规划/v1-技能规划/总览.md) | V1 版本规划与执行顺序 |
| [任务清单.md](docs/版本规划/v1-技能规划/任务清单.md) | V1 实现任务清单 |
| [系统架构.md](docs/版本规划/v1-技能规划/系统架构.md) | V1 系统架构设计 |
| [多轮对话-技术设计.md](docs/版本规划/v1-技能规划/多轮对话-技术设计.md) | 多轮对话技术方案 |


