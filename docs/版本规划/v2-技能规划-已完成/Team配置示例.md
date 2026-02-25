# Team 配置示例

本文档提供 OPC-CEO 系统中 Team 配置的完整示例和使用指南。

## 1. Team 配置概览

### 1.1 配置文件的作用

Team 配置文件定义了多个 Agent 协作完成复杂任务的规则和结构，包括：

- **团队名称和描述** - 标识团队用途
- **团队成员** - 参与协作的 Agent 及其角色
- **任务模板** - 预定义的任务分配模式
- **协作模式** - Agent 之间的通信和协调规则

### 1.2 配置位置和命名约定

**存储位置**：
```
~/.claude/teams/{team-name}.json
```

**命名约定**：
- 使用 kebab-case 格式（小写字母、数字、连字符）
- 描述性名称，反映团队用途
- 示例：`project-launch-team`, `finance-analysis-team`

**任务列表位置**：
```
~/.claude/tasks/{team-name}/
```

## 2. 配置文件格式

### 2.1 完整配置示例

```yaml
# Team: project-launch-team
team_name: project-launch-team
description: 新项目启动协作团队
agent_type: general-purpose
members:
  - name: task-manager
    role: 任务管理
    agent_path: .claude/agents/task-agent.md
    capabilities:
      - 创建任务
      - 更新任务状态
      - 分配任务
  - name: file-manager
    role: 文件管理
    agent_path: .claude/agents/file-agent.md
    capabilities:
      - 创建文档
      - 组织文件结构
      - 版本控制
  - name: knowledge-manager
    role: 知识管理
    agent_path: .claude/agents/knowledge-agent.md
    capabilities:
      - 存储知识点
      - 检索知识
      - 关联实体
task_templates:
  - name: 创建项目任务
    owner: task-manager
    description: 使用 task-agent 创建项目任务
    required_agents: [task-manager]
  - name: 创建项目文档
    owner: file-manager
    description: 使用 file-agent 创建项目文档
    required_agents: [file-manager]
  - name: 添加项目知识
    owner: knowledge-manager
    description: 使用 knowledge-agent 添加项目知识点
    required_agents: [knowledge-manager]
collaboration_rules:
  - rule: 任务创建后通知知识管理
    from: task-manager
    to: knowledge-manager
    trigger: task_created
  - rule: 文档创建后更新知识库
    from: file-manager
    to: knowledge-manager
    trigger: document_created
```

### 2.2 配置字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `team_name` | string | 是 | 团队唯一标识（kebab-case） |
| `description` | string | 是 | 团队用途描述 |
| `agent_type` | string | 是 | 团队领导者类型 |
| `members` | array | 是 | 成员 Agent 列表 |
| `task_templates` | array | 否 | 预定义任务模板 |
| `collaboration_rules` | array | 否 | Agent 协作规则 |

**成员 Agent 字段**：
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | Agent 名称（用于引用） |
| `role` | string | 是 | Agent 角色 |
| `agent_path` | string | 是 | Agent 定义文件路径 |
| `capabilities` | array | 否 | Agent 能力列表 |

**任务模板字段**：
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 任务名称 |
| `owner` | string | 是 | 负责人 Agent |
| `description` | string | 是 | 任务描述 |
| `required_agents` | array | 否 | 必需参与的 Agent |

## 3. 预定义 Team 模板

### 3.1 模板 1: project-launch-team

**用途**：启动新项目

**适用场景**：
- 新项目初始化
- 项目结构搭建
- 基础文档创建

**配置**：
```yaml
team_name: project-launch-team
description: 新项目启动协作团队
agent_type: general-purpose
members:
  - name: task-manager
    role: 任务管理
    agent_path: .claude/agents/task-agent.md
  - name: file-manager
    role: 文件管理
    agent_path: .claude/agents/file-agent.md
  - name: knowledge-manager
    role: 知识管理
    agent_path: .claude/agents/knowledge-agent.md
task_templates:
  - name: 创建项目任务
    owner: task-manager
    description: 使用 task-agent 创建项目任务
  - name: 创建项目文档
    owner: file-manager
    description: 使用 file-agent 创建项目文档
  - name: 添加项目知识
    owner: knowledge-manager
    description: 使用 knowledge-agent 添加项目知识点
collaboration_rules:
  - rule: 任务创建后通知知识管理
    from: task-manager
    to: knowledge-manager
    trigger: task_created
  - rule: 文档创建后更新知识库
    from: file-manager
    to: knowledge-manager
    trigger: document_created
```

### 3.2 模板 2: finance-analysis-team

**用途**：财务分析

**适用场景**：
- 交易记录分析
- 财务报表生成
- 预算规划

**配置**：
```yaml
team_name: finance-analysis-team
description: 财务分析协作团队
agent_type: general-purpose
members:
  - name: finance-manager
    role: 财务管理
    agent_path: .claude/agents/finance-agent.md
  - name: knowledge-manager
    role: 知识管理
    agent_path: .claude/agents/knowledge-agent.md
task_templates:
  - name: 记录交易
    owner: finance-manager
    description: 使用 finance-agent 记录交易
  - name: 生成财务报表
    owner: finance-manager
    description: 使用 finance-agent 生成报表
  - name: 分析财务趋势
    owner: finance-manager
    description: 使用 finance-agent 分析趋势
collaboration_rules:
  - rule: 交易记录后更新知识库
    from: finance-manager
    to: knowledge-manager
    trigger: transaction_recorded
```

### 3.3 模板 3: schedule-planning-team

**用途**：日程规划

**适用场景**：
- 日程安排
- 时间管理
- 任务时间规划

**配置**：
```yaml
team_name: schedule-planning-team
description: 日程规划协作团队
agent_type: general-purpose
members:
  - name: schedule-manager
    role: 日程管理
    agent_path: .claude/agents/schedule-agent.md
  - name: task-manager
    role: 任务管理
    agent_path: .claude/agents/task-agent.md
task_templates:
  - name: 创建日程事件
    owner: schedule-manager
    description: 使用 schedule-agent 创建事件
  - name: 安排任务时间
    owner: task-manager
    description: 使用 task-agent 安排任务时间
  - name: 冲突检测
    owner: schedule-manager
    description: 使用 schedule-agent 检测时间冲突
collaboration_rules:
  - rule: 任务安排后同步日程
    from: task-manager
    to: schedule-manager
    trigger: task_scheduled
```

### 3.4 模板 4: global-collaboration-team

**用途**：全局协作

**适用场景**：
- 复杂跨域任务
- 全局状态同步
- 系统级协调

**配置**：
```yaml
team_name: global-collaboration-team
description: 全局协作团队
agent_type: general-purpose
members:
  - name: task-manager
    role: 任务管理
    agent_path: .claude/agents/task-agent.md
  - name: file-manager
    role: 文件管理
    agent_path: .claude/agents/file-agent.md
  - name: knowledge-manager
    role: 知识管理
    agent_path: .claude/agents/knowledge-agent.md
  - name: finance-manager
    role: 财务管理
    agent_path: .claude/agents/finance-agent.md
  - name: schedule-manager
    role: 日程管理
    agent_path: .claude/agents/schedule-agent.md
task_templates:
  - name: 全局状态同步
    owner: opc-ceo-core
    description: 同步所有 Agent 的状态
  - name: 跨域任务协调
    owner: opc-ceo-core
    description: 协调跨多个领域的任务
collaboration_rules:
  - rule: 任务变更全局通知
    from: task-manager
    to: all
    trigger: task_changed
  - rule: 财务数据全局同步
    from: finance-manager
    to: all
    trigger: finance_updated
  - rule: 日程变更全局通知
    from: schedule-manager
    to: all
    trigger: schedule_changed
```

### 3.5 模板 5: automation-ops-team

**用途**：自动化运维

**适用场景**：
- 自动化脚本执行
- 系统监控
- 错误处理

**配置**：
```yaml
team_name: automation-ops-team
description: 自动化运维团队
agent_type: general-purpose
members:
  - name: automation-manager
    role: 自动化管理
    agent_path: .claude/agents/automation-agent.md
  - name: task-manager
    role: 任务管理
    agent_path: .claude/agents/task-agent.md
  - name: knowledge-manager
    role: 知识管理
    agent_path: .claude/agents/knowledge-agent.md
task_templates:
  - name: 执行自动化脚本
    owner: automation-manager
    description: 使用 automation-agent 执行脚本
  - name: 创建监控任务
    owner: task-manager
    description: 使用 task-agent 创建监控任务
  - name: 记录执行结果
    owner: knowledge-manager
    description: 使用 knowledge-agent 记录结果
collaboration_rules:
  - rule: 脚本执行后记录结果
    from: automation-manager
    to: knowledge-manager
    trigger: script_executed
```

## 4. 使用方式

### 4.1 CEO 选择模板创建 Team

CEO 在启动协作时，按以下步骤选择模板：

```
1. 分析任务需求
   ↓
2. 匹配合适的 Team 模板
   ↓
3. 加载模板配置
   ↓
4. 根据需求微调成员和规则
   ↓
5. 创建 Team 并启动协作
```

**示例对话**：
```
用户：启动一个新的财务分析任务

CEO：检测到财务分析需求
     - 选择模板：finance-analysis-team
     - 加载成员：finance-manager, knowledge-manager
     - 创建任务：分析本月交易记录

     [Team 创建成功]
     finance-manager: 正在分析交易记录...
     knowledge-manager: 已记录分析进度...
```

### 4.2 修改配置满足特定需求

根据实际需求，可以对模板进行以下修改：

**添加新成员**：
```yaml
members:
  - name: finance-manager
    role: 财务管理
    agent_path: .claude/agents/finance-agent.md
  - name: schedule-manager  # 新增
    role: 日程管理
    agent_path: .claude/agents/schedule-agent.md
```

**添加自定义任务模板**：
```yaml
task_templates:
  - name: 生成月度财务报告
    owner: finance-manager
    description: 分析本月交易并生成报告
    custom_params:
      time_range: month
      output_format: pdf
```

**修改协作规则**：
```yaml
collaboration_rules:
  - rule: 报告生成后创建会议事件
    from: finance-manager
    to: schedule-manager
    trigger: report_generated
    action: create_meeting_event
```

### 4.3 保存和重用 Team 配置

**保存自定义配置**：

方法 1：保存为新模板
```
~/.claude/teams/my-custom-team.yaml
```

方法 2：覆盖现有模板
```
~/.claude/teams/project-launch-team.yaml
```

**重用配置流程**：
```
1. 从 ~/.claude/teams/ 加载配置
   ↓
2. 验证成员 Agent 存在性
   ↓
3. 创建对应的任务列表目录
   ↓
4. 启动 Team 协作
   ↓
5. 执行完成后保存执行记录
```

### 4.4 最佳实践

1. **从模板开始** - 使用预定义模板作为起点
2. **按需精简** - 只添加必需的成员和规则
3. **命名清晰** - Team 名称应清晰反映用途
4. **文档化自定义** - 为自定义配置添加注释
5. **定期清理** - 删除不再使用的 Team 配置

## 5. 配置验证

创建 Team 时，系统会进行以下验证：

| 验证项 | 说明 |
|--------|------|
| 名称唯一性 | Team 名称必须唯一 |
| 成员存在性 | 所有成员 Agent 必须存在 |
| 路径有效性 | Agent 路径必须有效 |
| 规则一致性 | 协作规则中的 Agent 必须在成员列表中 |
| 循环依赖 | 避免循环依赖的协作规则 |

## 6. 故障排查

### 6.1 常见问题

**问题 1：Team 创建失败**
```
原因：名称已存在
解决：使用不同的 team_name
```

**问题 2：Agent 加载失败**
```
原因：agent_path 不正确
解决：检查 .claude/agents/ 目录结构
```

**问题 3：协作规则不生效**
```
原因：trigger 事件未触发
解决：检查 trigger 名称是否正确
```

### 6.2 调试方法

1. **查看 Team 配置**：
   ```bash
   cat ~/.claude/teams/{team-name}.json
   ```

2. **检查任务列表**：
   ```bash
   ls ~/.claude/tasks/{team-name}/
   ```

3. **验证 Agent 状态**：
   ```bash
   # 通过 CEO Agent 查询成员状态
   ```

## 7. 相关文档

- [设计意图](../../plans/v1-技能规划/设计意图.md) - Team 架构设计原则
- [角色设计](../../plans/v1-技能规划/角色设计.md) - Agent 角色定义
- [总览](../../plans/v1-技能规划/总览.md) - 系统整体规划
- [Team协作架构](./Team协作架构.md) - Team 协作架构详解
