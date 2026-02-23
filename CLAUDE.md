# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

**OPC-CEO** 是一人公司的 CEO Agent 系统，基于 Claude Code Skills/Agents 实现。

## 设计原则

1. **Agent 和 Skill 优先** - 详见 [设计意图](plans/v1-技能规划/设计意图.md)
2. **MCP Memory 作为数据层** - 所有数据存储在知识图谱中
3. **统一入口，角色分工** - CEO 协调，各专业角色各司其职

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

| 类型 | 格式 | 示例 |
|------|------|------|
| 任务 | `TASK-YYYY-MM-DD-NNN` | `TASK-2026-02-23-001` |
| 项目 | `PROJ-NNN` | `PROJ-001` |
| 交易 | `TXN-YYYY-MM-DD-NNN` | `TXN-2026-02-23-001` |
| 事件 | `EVENT-YYYY-MM-DD-NNN` | `EVENT-2026-02-24-001` |

## 默认配置

| 配置项 | 值 |
|--------|-----|
| Git 项目目录 | `E:\repository_git` |
| 文档命名规范 | **使用中文命名** |
| 临时目录 | `tmp/` - 思考古迹，非正式文档 |

## Skill 创建规范

创建 Skill 时必须遵循以下命名规则：

| 文件类型 | 命名规则 | 示例 |
|----------|----------|------|
| 主入口 | `SKILL.md`（固定） | `SKILL.md` |
| 功能模块 | **中文命名** | `任务操作.md`、`项目管理.md` |
| 快速参考 | `快速参考.md` | `快速参考.md` |

**禁止使用**英文模块名如 `task-operations.md`，必须使用中文 `任务操作.md`

## 实现状态

- ✅ `devops-engineer` - 运维支撑
- 📋 关键路径：`opc-ceo-core`, `task-manager`, `file-manager`, `claude-sdk-executor`
- 📋 后续：`knowledge-manager`, `finance-manager`, `schedule-manager`, `automation-manager`

## 关键文档

| 文档 | 用途 |
|------|------|
| `设计意图.md` | 设计原则、技术决策依据、验收标准 |
| `模板规范.md` | Skill 格式、实体定义、命名规范 |
| `角色设计.md` | 8 个技能的详细设计 |
| `总览.md` | V1 版本规划与执行顺序 |
| `任务清单.md` | 实现任务清单 |


