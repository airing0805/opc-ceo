# 角色设计索引

> **注意**：此目录属于 V1 版本规划，已于 2026-02-24 废弃。
>
> V1 基于纯 Skills 架构，V2 已转向原生 Team/SendMessage API 协作架构。
>
> 当前版本请参考：[V2 规划总览](../../v2-技能规划/README.md)
>
> 原有 Skills 已归档至：`.claude/skills/disabled/`

---

本目录包含 OPC-CEO 系统所有角色的详细设计文档（已废弃）。

## 目录结构

```
角色设计/
├── README.md                      # 本索引文件
│
├── 01-opc-ceo-core.md            # CEO 核心控制
├── 02-task-manager.md            # 任务管理专家
├── 03-file-manager.md            # 文件管理专家
├── 04-knowledge-manager.md       # 知识管理专家
├── 05-finance-manager.md         # 财务管理专家
├── 06-schedule-manager.md        # 日程管理专家
├── 07-automation-manager.md      # 自动化专家
├── 08-claude-sdk-executor.md     # Claude SDK 执行器
├── 09-wellness-coach.md          # 心理咨询师
│
└── ceo-coach.md                  # CEO 外部评估教练
```

## 角色分类

### 核心角色 (Core Roles)

| 编号 | 角色名 | 职责 | 优先级 |
|------|--------|------|--------|
| 01 | [opc-ceo-core](./01-opc-ceo-core.md) | CEO 总控，决策协调 | 关键 |
| 02 | [task-manager](./02-task-manager.md) | 任务全生命周期管理 | 关键 |
| 03 | [file-manager](./03-file-manager.md) | 文件系统操作 | 关键 |
| 08 | [claude-sdk-executor](./08-claude-sdk-executor.md) | SDK/API 程序化执行 | 关键 |

### 管理角色 (Management Roles)

| 编号 | 角色名 | 职责 | 优先级 |
|------|--------|------|--------|
| 04 | [knowledge-manager](./04-knowledge-manager.md) | 知识库构建维护 | 高 |
| 05 | [finance-manager](./05-finance-manager.md) | 财务记录分析 | 中 |
| 06 | [schedule-manager](./06-schedule-manager.md) | 日程时间管理 | 中 |
| 07 | [automation-manager](./07-automation-manager.md) | 工作流自动化 | 中 |

### 支撑角色 (Support Roles)

| 编号 | 角色名 | 职责 | 优先级 |
|------|--------|------|--------|
| 09 | [wellness-coach](./09-wellness-coach.md) | 心理健康支持 | 高 |

## 教练角色体系

每个执行角色都有对应的教练角色，负责：

- **设计指导**：定义角色能力边界和工作流程
- **行为优化**：分析执行效果，提出改进建议
- **能力扩展**：评估新功能，设计扩展路径

### 教练角色

**说明**：V1 架构演进过程中，CEO 内置了教练能力，承担了下属角色的教练职责。原有的独立教练角色文档未实际创建。仅保留 `ceo-coach` 作为 CEO 的外部评估教练。

| 教练角色 | 对应执行角色 | 状态 |
|----------|--------------|------|
| [ceo-coach](./ceo-coach.md) | opc-ceo-core | 已创建 |
| 教练-task-manager | task-manager | 未创建（由 CEO 承担） |
| 教练-file-manager | file-manager | 未创建（由 CEO 承担） |
| 教练-knowledge-manager | knowledge-manager | 未创建（由 CEO 承担） |
| 教练-finance-manager | finance-manager | 未创建（由 CEO 承担） |
| 教练-schedule-manager | schedule-manager | 未创建（由 CEO 承担） |
| 教练-automation-manager | automation-manager | 未创建（由 CEO 承担） |
| 教练-claude-sdk-executor | claude-sdk-executor | 未创建（由 CEO 承担） |
| 教练-wellness-coach | wellness-coach | 未创建（由 CEO 承担） |

## 角色架构图

```
                    ┌─────────────────────────────────────────────────────┐
                    │                   教练角色层                          │
                    │  (设计/指导/优化 - 不直接参与执行)                      │
                    └───────────────────────────┬─────────────────────────┘
                                                │ 指导
                    ┌───────────────────────────▼─────────────────────────┐
                    │                   执行角色层                          │
                    │                                                      │
                    │                  CEO (opc-ceo-core)                  │
                    │                        │                             │
                    │    ┌───────────────────┼───────────────────┐        │
                    │    │                   │                   │        │
                    │    ▼                   ▼                   ▼        │
                    │ task-manager     file-manager     knowledge-manager │
                    │    │                   │                   │        │
                    │    └───────────────────┼───────────────────┘        │
                    │                        │                             │
                    │    ┌───────────────────┼───────────────────┐        │
                    │    │                   │                   │        │
                    │    ▼                   ▼                   ▼        │
                    │ finance-manager  schedule-manager  automation-manager│
                    │                        │                             │
                    │                        ▼                             │
                    │              claude-sdk-executor                      │
                    │                                                      │
                    │    ┌───────────────────────────────────────────┐    │
                    │    │         wellness-coach (横向支撑)            │    │
                    │    └───────────────────────────────────────────┘    │
                    │                                                      │
                    └──────────────────────────────────────────────────────┘
```

## 文档规范

### 角色文档结构

每个角色文档应包含：

1. **角色定位**：简明扼要的角色描述
2. **能力要求**：该角色需要具备的能力
3. **技能文件**：对应的技能文件列表
4. **核心职责/功能**：详细的功能说明

## 更新历史

| 日期 | 变更内容 |
|------|----------|
| 2026-02-23 | 初始创建：拆分角色设计、添加教练体系、添加心理咨询师角色 |
