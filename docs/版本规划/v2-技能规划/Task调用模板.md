# Task 调用模板

本文档提供 CEO 直接使用 Task 工具调用各 agents 的标准模板。

---

## 基本调用格式

```json
{
  "subagent_type": "general-purpose",
  "prompt": "明确的任务描述",
  "description": "简短描述（3-5个词）"
}
```

**参数说明：**
- `subagent_type`: Agent 类型，通常是 `general-purpose`（支持所有工具的通用 agent）
- `prompt`: 具体任务指令，参考下文各 Agent 的 Prompt 模板
- `description`: 简短的任务描述，用于日志追踪

---

## 各 Agent 的 Prompt 模板

### Task Agent 模板

**Agent 路径：** `.claude/agents/task-agent.md`

**标准 Prompt：**

```
参考 task-agent (.claude/agents/task-agent.md) 执行任务：
{具体操作}

输入参数：
- 任务标题：{标题}
- 任务描述：{描述}
- 优先级：{高/中/低}
- 截止日期：{YYYY-MM-DD}
- 关联项目：{PROJ-NNN}
- 关联任务：{TASK-YYYY-MM-DD-NNN}
```

**操作示例：**

```
参考 task-agent (.claude/agents/task-agent.md) 执行任务：
创建新任务并分配 ID

输入参数：
- 任务标题：完成季度财务报告
- 任务描述：收集并汇总 Q1 财务数据，生成分析报告
- 优先级：高
- 截止日期：2026-03-31
- 关联项目：PROJ-001
```

**常用操作：**
- 创建任务
- 更新任务状态
- 查询任务列表
- 删除任务
- 关联子任务

---

### File Agent 模板

**Agent 路径：** `.claude/agents/file-agent.md`

**标准 Prompt：**

```
参考 file-agent (.claude/agents/file-agent.md) 执行任务：
{具体操作}

输入参数：
- 文件类型：{文档/代码/配置/数据}
- 文件内容：{内容或模板}
- 保存路径：{相对或绝对路径}
- 格式要求：{Markdown/JSON/Python 等}
```

**操作示例：**

```
参考 file-agent (.claude/agents/file-agent.md) 执行任务：
创建项目文档

输入参数：
- 文件类型：文档
- 文件内容：# 项目名称\n\n## 目标\n{项目目标}\n\n## 计划\n{实施计划}
- 保存路径：docs/projects/proj-001-overview.md
- 格式要求：Markdown
```

**常用操作：**
- 创建文档
- 更新文件
- 读取文件
- 删除文件
- 文件夹管理

---

### Knowledge Agent 模板

**Agent 路径：** `.claude/agents/knowledge-agent.md`

**标准 Prompt：**

```
参考 knowledge-agent (.claude/agents/knowledge-agent.md) 执行任务：
{具体操作}

输入参数：
- 实体名称：{实体名}
- 实体类型：{任务/项目/知识/事件等}
- 观察内容：{观察列表}
- 关系类型：{关联/依赖/包含等}
- 关联实体：{关联实体名}
```

**操作示例：**

```
参考 knowledge-agent (.claude/agents/knowledge-agent.md) 执行任务：
创建新实体并添加观察

输入参数：
- 实体名称：Claude Code 使用技巧
- 实体类型：知识
- 观察内容：["Task工具可以并行调用多个agents", "MCP Memory用于存储知识图谱", "Claude SDK支持程序化执行"]
```

**常用操作：**
- 创建实体
- 添加观察
- 创建关系
- 查询实体
- 搜索知识

---

### Finance Agent 模板

**Agent 路径：** `.claude/agents/finance-agent.md`

**标准 Prompt：**

```
参考 finance-agent (.claude/agents/finance-agent.md) 执行任务：
{具体操作}

输入参数：
- 交易类型：{收入/支出/转账}
- 金额：{数值}
- 类别：{类别}
- 描述：{交易描述}
- 日期：{YYYY-MM-DD}
- 关联项目：{PROJ-NNN}
```

**操作示例：**

```
参考 finance-agent (.claude/agents/finance-agent.md) 执行任务：
记录新交易

输入参数：
- 交易类型：支出
- 金额：299.00
- 类别：工具订阅
- 描述：GitHub Copilot 月度订阅
- 日期：2026-02-24
- 关联项目：PROJ-001
```

**常用操作：**
- 记录交易
- 查询交易记录
- 生成财务报表
- 预算管理
- 分类分析

---

### Schedule Agent 模板

**Agent 路径：** `.claude/agents/schedule-agent.md`

**标准 Prompt：**

```
参考 schedule-agent (.claude/agents/schedule-agent.md) 执行任务：
{具体操作}

输入参数：
- 事件标题：{标题}
- 事件类型：{会议/任务/提醒等}
- 开始时间：{YYYY-MM-DD HH:MM}
- 结束时间：{YYYY-MM-DD HH:MM}
- 描述：{事件描述}
- 关联任务：{TASK-YYYY-MM-DD-NNN}
```

**操作示例：**

```
参考 schedule-agent (.claude/agents/schedule-agent.md) 执行任务：
创建日程事件

输入参数：
- 事件标题：项目评审会议
- 事件类型：会议
- 开始时间：2026-02-25 14:00
- 结束时间：2026-02-25 15:30
- 描述：Q1 项目进度评审，讨论里程碑达成情况
- 关联任务：TASK-2026-02-24-005
```

**常用操作：**
- 创建日程事件
- 更新日程
- 查询日程
- 设置提醒
- 冲突检测

---

## 并行调用示例

```markdown
# 并行调用多个 agents（无依赖关系）

同时启动：
- Agent 1: task-agent - 创建任务
  {
    "subagent_type": "general-purpose",
    "prompt": "参考 task-agent 创建任务：任务标题='设计系统架构'，优先级='高'，截止日期='2026-02-28'",
    "description": "创建架构设计任务"
  }

- Agent 2: file-agent - 创建文档文件
  {
    "subagent_type": "general-purpose",
    "prompt": "参考 file-agent 创建文档：路径='docs/architecture.md'，类型='文档'，内容='# 系统架构\\n\\n## 组件图'",
    "description": "创建架构文档"
  }

- Agent 3: finance-agent - 记录交易
  {
    "subagent_type": "general-purpose",
    "prompt": "参考 finance-agent 记录交易：类型='支出'，金额='500'，类别='办公用品'，描述='购买白板'，日期='2026-02-24'",
    "description": "记录采购交易"
  }
```

**何时使用并行调用：**
- 多个独立操作
- 无先后依赖关系
- 需要加快执行速度

---

## 串行调用示例

```markdown
# 串行调用（有依赖关系）

1. Agent 1: knowledge-agent - 检索知识
   {
     "subagent_type": "general-purpose",
     "prompt": "参考 knowledge-agent 搜索知识：查询='项目管理最佳实践'，返回=实体列表和观察内容",
     "description": "检索项目管理知识"
   }
   → 等待结果，获得知识内容

2. Agent 2: task-agent - 创建任务（基于知识结果）
   {
     "subagent_type": "general-purpose",
     "prompt": "参考 task-agent 创建任务：标题='应用项目管理最佳实践'，描述='根据检索到的最佳实践，优化当前项目流程'，优先级='中'",
     "description": "创建优化任务"
   }
   → 等待结果，获得任务 ID

3. Agent 3: file-agent - 生成文档（基于任务结果）
   {
     "subagent_type": "general-purpose",
     "prompt": "参考 file-agent 创建文档：路径='docs/optimization-plan.md'，内容='# 优化计划\\n\\n关联任务：TASK-2026-02-24-XXX\\n\\n## 实施步骤'",
     "description": "生成优化计划文档"
   }
```

**何时使用串行调用：**
- 后续操作依赖前一步结果
- 需要传递数据或状态
- 有明确的执行顺序

---

## 混合调用示例

```markdown
# 混合调用（部分并行 + 部分串行）

阶段 1：并行执行（无依赖）
- Agent 1: task-agent - 创建任务
- Agent 2: finance-agent - 记录预算

阶段 2：等待阶段 1 完成

阶段 3：串行执行（依赖阶段 1）
- Agent 3: knowledge-agent - 关联知识到任务
- Agent 4: file-agent - 生成任务文档

阶段 4：通知（所有完成）
- Agent 5: schedule-agent - 安排回顾会议
```

---

## 调用最佳实践

### 1. 明确任务目标

在调用前，明确：
- 需要哪个 Agent 处理？
- 具体执行什么操作？
- 需要哪些输入参数？
- 期望什么输出结果？

### 2. 选择调用模式

| 场景 | 调用模式 | 理由 |
|------|----------|------|
| 独立操作 | 并行 | 加速执行 |
| 依赖操作 | 串行 | 确保数据正确性 |
| 复杂流程 | 混合 | 平衡速度与准确性 |

### 3. 参数规范化

始终提供完整参数：
- 日期格式统一：`YYYY-MM-DD` 或 `YYYY-MM-DD HH:MM`
- ID 格式遵循：`TASK-YYYY-MM-DD-NNN`、`PROJ-NNN`
- 金额使用数值（不包含货币符号）
- 枚举值使用预定义选项

### 4. 错误处理

如果 Agent 返回错误：
1. 检查参数是否完整
2. 验证格式是否正确
3. 确认 Agent 路径是否正确
4. 必要时重试或回滚

### 5. 日志记录

每个调用使用清晰的 `description`：
- 3-5 个词描述
- 便于后续追踪和审计
- 例如：`"创建架构任务"`、`"记录采购交易"`

---

## 完整调用流程示例

```markdown
# 场景：启动新项目并记录相关信息

1. knowledge-agent - 检索项目模板知识
   → 获得项目结构模板

2. task-agent - 创建主任务
   → 获得 TASK-2026-02-24-001

3. task-agent - 创建子任务（并行）
   - 子任务 A：TASK-2026-02-24-002（需求分析）
   - 子任务 B：TASK-2026-02-24-003（架构设计）
   - 子任务 C：TASK-2026-02-24-004（开发实现）

4. file-agent - 创建项目文档（并行）
   - docs/proj-001-overview.md（项目总览）
   - docs/proj-001-requirements.md（需求文档）
   - docs/proj-001-architecture.md（架构文档）

5. schedule-agent - 安排里程碑会议
   → 创建项目启动会事件

6. finance-agent - 记录项目预算
   → 创建初始预算记录

7. knowledge-agent - 关联所有实体
   → 建立项目、任务、文档、预算之间的关系图谱
```

---

## 附录：Agent 路径索引

| Agent | 路径 |
|-------|------|
| task-agent | `.claude/agents/task-agent.md` |
| file-agent | `.claude/agents/file-agent.md` |
| knowledge-agent | `.claude/agents/knowledge-agent.md` |
| finance-agent | `.claude/agents/finance-agent.md` |
| schedule-agent | `.claude/agents/schedule-agent.md` |
| automation-agent | `.claude/agents/automation-agent.md` |

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-02-24 | 初始版本，提供基础调用模板 |
