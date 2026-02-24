# 角色设计索引

本目录包含 OPC-CEO 系统所有角色的详细设计文档。

## 目录结构

```
角色设计/
├── README.md                      # 本索引文件
│
├── 01-opc-ceo-core.md            # CEO 核心控制
├── 教练-01-opc-ceo-core.md       # 教练 - CEO 核心控制
│
├── 02-task-manager.md            # 任务管理专家
├── 教练-02-task-manager.md       # 教练 - 任务管理
│
├── 03-file-manager.md            # 文件管理专家
├── 教练-03-file-manager.md       # 教练 - 文件管理
│
├── 04-knowledge-manager.md       # 知识管理专家
├── 教练-04-knowledge-manager.md  # 教练 - 知识管理
│
├── 05-finance-manager.md         # 财务管理专家
├── 教练-05-finance-manager.md    # 教练 - 财务管理
│
├── 06-schedule-manager.md        # 日程管理专家
├── 教练-06-schedule-manager.md   # 教练 - 日程管理
│
├── 07-automation-manager.md      # 自动化专家
├── 教练-07-automation-manager.md # 教练 - 自动化
│
├── 08-claude-sdk-executor.md     # Claude SDK 执行器
├── 教练-08-claude-sdk-executor.md# 教练 - SDK 执行器
│
├── 09-wellness-coach.md          # 心理咨询师
└── 教练-09-wellness-coach.md     # 教练 - 心理咨询
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

### 教练角色列表

| 教练角色 | 对应执行角色 |
|----------|--------------|
| [ceo-coach](../../.claude/skills/ceo-coach/SKILL.md) | opc-ceo-core |
| [教练-02-task-manager](./教练-02-task-manager.md) | task-manager |
| [教练-03-file-manager](./教练-03-file-manager.md) | file-manager |
| [教练-04-knowledge-manager](./教练-04-knowledge-manager.md) | knowledge-manager |
| [教练-05-finance-manager](./教练-05-finance-manager.md) | finance-manager |
| [教练-06-schedule-manager](./教练-06-schedule-manager.md) | schedule-manager |
| [教练-07-automation-manager](./教练-07-automation-manager.md) | automation-manager |
| [教练-08-claude-sdk-executor](./教练-08-claude-sdk-executor.md) | claude-sdk-executor |
| [教练-09-wellness-coach](./教练-09-wellness-coach.md) | wellness-coach |

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
5. **教练角色**：指向对应教练文档的链接

### 教练文档结构

每个教练文档应包含：

1. **教练角色定位**：教练的职责范围
2. **教练职责**：具体指导领域
3. **指导领域**：关注的优化方向
4. **评估指标**：衡量效果的指标
5. **指导原则**：教练应遵循的原则

## 更新历史

| 日期 | 变更内容 |
|------|----------|
| 2026-02-23 | 初始创建：拆分角色设计、添加教练体系、添加心理咨询师角色 |
