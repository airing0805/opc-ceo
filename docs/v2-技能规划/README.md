# V2 - Agent 协作系统

## 版本规划

| 版本 | 阶段 | 目标 | 状态 |
|------|------|------|------|
| v2.1 | 阶段1 | 创建自定义 Agents | ✅ 已完成 |
| v2.2 | 阶段2 | 直接使用 Task 工具 | ✅ 已完成 |
| v2.3 | 阶段3 | Team 协作模式 | ✅ 已完成 |
| v2.4 | 阶段4 | 文档沟通规范 | ✅ 已完成 |

## 背景

**问题来源**：尝试通过 `claude-sdk-executor` 实现 agent 调用 agent，但遇到 SDK 嵌套检测限制。

**解决方案**：利用 Claude Code 原生的 Task 工具和 Team/TaskList 系统实现 agent 协作。

**技术对比**：

| OpenClaw 机制 | Claude Code 对应 |
|--------------|-----------------|
| sessions_spawn 工具 | **Task 工具** |
| Subagent Registry | **TaskList + TaskUpdate** |
| Command Lane | Task 的 subagent_type |
| Announce | Team 的 SendMessage |

---

## OpenClaw Agent 调用机制

| 机制 | 说明 |
|------|------|
| sessions_spawn 工具 | 作为 LLM 工具暴露给 agent，允许直接调用 |
| Command Lane 队列 | main/cron/subagent/nested 四种 lane 隔离执行 |
| Subagent Registry | 追踪所有子 agent 的 runId、sessionKey、状态 |
| Announce 机制 | 子 agent 完成后自动回传结果给主 agent |
| 系统提示词注入 | 为子 agent 注入特定的行为约束和职责 |
| 安全性 | 子 agent 不能 spawn 子 agent，防止无限嵌套 |
| 配置 | allowAgents 白名单控制跨 agent 调用 |

---

## Claude Code 原生 Agent 能力

| 能力 | 说明 |
|------|------|
| Task 工具 | 启动子 agent 执行任务，支持多种 subagent_type |
| subagent_type | Explore, Plan, general-purpose, code-reviewer 等 |
| TeamCreate | 创建团队进行多 agent 协作 |
| TaskList/TaskUpdate | 任务状态追踪 |
| SendMessage | agent 间通信 |
| 特点 | 无嵌套限制，原生支持 agent 调用 agent |

---

## Task 工具调用模板

| 操作 | subagent_type | prompt 模板 |
|------|--------------|-------------|
| 创建任务 | general-purpose | `参考 task-manager skill，使用 MCP Memory 创建任务：{title}` |
| 查询任务 | general-purpose | `参考 task-manager skill，搜索任务：{query}` |
| 文件操作 | general-purpose | `参考 file-manager skill，{操作}：{参数}` |
| 代码探索 | Explore | `分析项目结构...` |
| 规划设计 | Plan | `设计实现方案...` |
| 代码审查 | code-reviewer | `审查这段代码...` |

---

## v2.1 - 创建自定义 Agents

**目标**：将现有 Skills 映射为 Claude Code Agents

**目录**：`.claude/agents/`

### Agent 定义

| Agent | 来源 Skill | 工具权限 | 职责 |
|-------|-----------|---------|------|
| task-agent | task-manager | mcp__memory__*, Read, Glob, Grep | 任务 CRUD |
| file-agent | file-manager | Read, Write, Edit, Glob, Grep, Bash | 文件操作 |
| knowledge-agent | knowledge-manager | mcp__memory__* | 知识管理 |
| finance-agent | finance-manager | mcp__memory__* | 财务操作 |
| schedule-agent | schedule-manager | mcp__memory__* | 日程操作 |

### 任务清单

- [x] 2.1.1 创建 task-agent.md
- [x] 2.1.2 创建 file-agent.md
- [x] 2.1.3 创建 knowledge-agent.md
- [x] 2.1.4 创建 finance-agent.md
- [x] 2.1.5 创建 schedule-agent.md
- [x] 2.1.6 更新 CEO 调用规范

---

## v2.2 - 直接使用 Task 工具

**目标**：不创建新 agent 文件，CEO 直接使用 Task 工具 + 现有 skill 文档

### 任务清单

- [x] 2.2.1 设计 Task 调用模板
- [x] 2.2.2 创建调用模板文档
- [x] 2.2.3 验证 Task 调用流程

---

## v2.3 - Team 协作模式

**目标**：使用 Team + TaskList 实现多 agent 并行协作

### 任务清单

- [x] 2.3.1 设计 Team 协作架构
- [x] 2.3.2 创建 Team 配置
- [x] 2.3.3 设计 SendMessage 协作
- [x] 2.3.4 验证 Team 协作流程

---

## v2.4 - 文档沟通规范

**目标**：建立文档沟通规范，所有角色间沟通通过 MD 文档，留下痕迹供用户查看

**背景**：用户差评反馈要求
1. CEO 不应该从 README 找任务执行
2. 所有角色的沟通必须通过 MD 文档
3. 每个角色可以定期更新自己的 memory
4. 角色间沟通必须通过文档
5. 我与 CEO 的沟通内容用文档记录
6. 公司运营的内容都通过文档沟通，留下痕迹
7. 用户必须能看到所有痕迹

### 文档目录结构

```
docs/v2-技能规划/沟通文档/
├── 文档沟通规范.md          # 本规范
├── 任务分配.md              # CEO 分配给各角色的任务
├── 汇报总结.md              # 各角色向 CEO 的汇报
├── 协调记录.md              # 跨角色协调记录
├── CEO-用户沟通.md          # CEO 与用户的对话记录
├── 角色记忆更新.md          # 各角色更新自己 memory 的记录
└── 工作日志/
    └── 2026-02-24.md        # 每日工作日志
```

### 任务清单

- [x] 2.4.1 创建文档沟通规范
- [x] 2.4.2 创建沟通文档目录结构
- [x] 2.4.3 更新 CEO SKILL.md
- [x] 2.4.4 更新 README.md
- [ ] 2.4.5 测试文档沟通流程

---

## 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    CEO (opc-ceo-core)                           │
│  决策协调、任务分发、结果验收                                     │
└────────────────────┬────────────────────────────────────────────┘
                     │
         ┌───────────┼───────────┬───────────────┐
         │           │           │               │
         ▼           ▼           ▼               ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐   ┌──────────┐
    │  Task   │ │  Task   │ │  Task   │   │   Team   │
    │ 工具调用 │ │ 工具调用 │ │ 工具调用 │   │ 并行协作  │
    └────┬────┘ └────┬────┘ └────┬────┘   └────┬─────┘
         │           │           │              │
         ▼           ▼           ▼              ▼
    ┌─────────────────────────────────────────────────┐
    │              Claude Code Subagent               │
    │  - task-agent (任务操作)                         │
    │  - file-agent (文件操作)                         │
    │  - knowledge-agent (知识管理)                    │
    │  - finance-agent (财务操作)                      │
    │  - schedule-agent (日程操作)                     │
    └─────────────────────────────────────────────────┘
```

---

## 进度统计

| 版本 | 总任务数 | 已完成 | 进度 |
|------|----------|--------|------|
| v2.1 | 6 | 6 | **100%** |
| v2.2 | 3 | 3 | **100%** |
| v2.3 | 4 | 4 | **100%** |
| v2.4 | 5 | 4 | **80%** |
| **总计** | **18** | **17** | **94%** |

---

## 创建信息

- 创建日期：2026-02-24
- 创建方式：从 MCP Memory 迁移到文件
