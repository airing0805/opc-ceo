# OPC-CEO 24小时自我进化方案

> 基于 PM2 + Claude Code 24h-Integration 的持续改进机制

---

## 1. 方案概述

### 1.1 核心理念

**"系统自我修复、能力自我提升、架构自我演进"**

通过 PM2 进程管理器保持 Claude Code 24/7 运行，通过任务队列 (`queue.json`) 与各角色沟通，实现自动化任务调度和执行。

### 1.2 设计目标

| 目标 | 描述 | 指标 |
|------|------|------|
| 全天候运行 | 24/7 自动化任务处理 | 运行时间占比 > 99% |
| 自我评估 | 定期分析系统表现和数据 | 每日产出评估报告 |
| 持续优化 | 自动识别改进点并执行 | 每周完成至少2项优化 |
| 队列管理 | 任务数 >10 时暂停新任务分配 | 队列峰值控制 |

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PM2 进程守护层                                  │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  claude-runner (auto-runner.js)                            │   │
│  │  工作目录: E:\workspaces_2026_python\claude_code_cookbook\ │   │
│  │            claude-code-24h-integration                    │   │
│  └──────────────────┬─────────────────────────────────────────┘   │
└─────────────────────┼───────────────────────────────────────────────┘
                      │
          ┌───────────┼───────────┐
          │           │           │
          ▼           ▼           ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐
    │ 定时任务 │ │ 队列任务 │ │ 队列状态 │
    │scheduled│ │  queue  │ │ 检查    │
    │  .json  │ │  .json  │ │ >10暂停 │
    └─────────┘ └─────────┘ └─────────┘
          │           │
          └─────┬─────┘
                ▼
         ┌──────────────┐
         │ Claude Code  │
         │   CLI 执行   │
         └──────────────┘
                │
      ┌─────────┴─────────┐
      │                   │
      ▼                   ▼
  ceo-coach           opc-ceo-core
  (教练)              (执行者)
```

### 2.2 核心组件

| 组件 | 位置 | 说明 |
|------|------|------|
| **PM2** | 全局安装 | 进程守护，24/7 运行 |
| **auto-runner.js** | claude-code-24h-integration/src/ | 任务调度器核心 |
| **queue.json** | claude-code-24h-integration/tasks/ | 待执行任务队列 |
| **scheduled.json** | claude-code-24h-integration/tasks/ | 定时任务配置 |
| **completed.json** | claude-code-24h-integration/tasks/ | 已完成任务记录 |
| **failed.json** | claude-code-24h-integration/tasks/ | 失败任务记录 |
| **queue-manager** | .claude/skills/queue-manager/ | 队列管理 Skill |

---

## 3. PM2 配置与使用

### 3.1 工作目录

```
E:\workspaces_2026_python\claude_code_cookbook\claude-code-24h-integration
```

### 3.2 PM2 安装位置

PM2 需要全局安装：

```bash
npm install -g pm2
```

验证安装：
```bash
pm2 --version
```

### 3.3 启动服务

**Windows 用户（推荐）：**

```bash
cd E:\workspaces_2026_python\claude_code_cookbook\claude-code-24h-integration
scripts\start-pm2.bat
```

**或使用 PM2 命令：**

```bash
cd E:\workspaces_2026_python\claude_code_cookbook\claude-code-24h-integration
pm2 start ecosystem.config.js
pm2 save
```

### 3.4 PM2 常用命令

| 命令 | 说明 |
|------|------|
| `pm2 status` | 查看运行状态 |
| `pm2 logs claude-runner` | 查看实时日志 |
| `pm2 restart claude-runner` | 重启服务 |
| `pm2 stop claude-runner` | 停止服务 |
| `pm2 delete claude-runner` | 删除服务 |
| `pm2 save` | 保存状态（开机自启） |
| `pm2 startup` | 配置开机自启 |
| `pm2 flush` | 清空日志 |
| `pm2 monit` | 实时监控资源 |

### 3.5 PM2 配置文件

`ecosystem.config.js` 关键配置：

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `name` | `claude-runner` | 进程名称 |
| `script` | `./src/auto-runner.js` | 执行脚本 |
| `cwd` | `E:\workspaces_2026_python\claude_code_cookbook\claude-code-24h-integration` | 工作目录 |
| `autorestart` | `true` | 进程崩溃自动重启 |
| `max_restarts` | `30` | 最大重启次数 |
| `restart_delay` | `10000` | 重启延迟 10秒 |
| `max_memory_restart` | `5000M` | 内存超过 5GB 自动重启 |
| `cron_restart` | `'0 12 * * *'` | 每天 12:00 定时重启 |

---

## 4. 任务队列机制

### 4.1 队列文件结构

#### queue.json（待执行任务）

```json
{
  "list": [
    {
      "id": "task-1234567890",
      "prompt": "你是 ceo-coach。任务：分析当前项目需要优化和改进的内容...",
      "workspace": "E:\\workspaces_2026_python\\OPC-CEO",
      "timeout": 1200000,
      "autoApprove": true,
      "allowedTools": [],
      "scheduled": true,
      "scheduledId": "opc-coach-planning"
    }
  ]
}
```

#### scheduled.json（定时任务配置）

```json
{
  "tasks": [
    {
      "id": "opc-coach-planning",
      "name": "Coach 规划任务",
      "cron": "1 */1 * * *",
      "prompt": "你是 ceo-coach。任务：分析当前项目...",
      "workspace": "E:\\workspaces_2026_python\\OPC-CEO",
      "enabled": false,
      "lastRun": "2026-02-26T06:01:04",
      "nextRun": "2026-02-26 07:01:00"
    }
  ]
}
```

### 4.2 任务调度流程

```
每 10 秒轮询:
  │
  ├── 检查 scheduled.json 是否有定时任务到期
  │     │
  │     ├── 到期 → 创建任务副本 → 添加到 queue.json
  │     │          更新 lastRun 和 nextRun
  │     │
  │     └── 未到期 → 跳过
  │
  ├── 检查 queue.json 是否有任务
  │     │
  │     ├── 有任务 → 取第一个任务 → 写入 running.json
  │     │            执行 Claude Code CLI
  │     │            成功 → completed.json
  │     │            失败 → 重试2次 → failed.json
  │     │            从 queue.json 删除
  │     │
  │     └── 无任务 → 继续等待
  │
  └── 循环
```

### 4.3 队列管理策略

#### 队列阈值控制

| 队列状态 | 动作 |
|----------|------|
| 队列任务 ≤ 10 | 正常安排新任务 |
| 队列任务 > 10 | 暂停安排新任务给其他角色 |
| 队列任务 ≤ 5 | 恢复正常安排 |

**实现方式**: 通过 `queue-manager` Skill 检查队列状态并控制任务分配。

---

## 5. 进化周期设计

### 5.1 每日进化循环

**触发方式**: 通过 scheduled.json 配置定时任务

**任务列表**:

| ID | 角色 | Cron | 描述 |
|----|------|-------|------|
| opc-coach-planning | ceo-coach | 每小时 | 分析项目优化点，生成任务 |
| opc-coach-planning2 | ceo-coach | 每小时 | 自我进化 |
| opc-ceo-execution | ceo 执行者 | 每小时 | 执行任务分配.md 中的任务 |
| opc-ceo-execution2 | ceo 执行者 | 每小时 | 自我进化 |

### 5.2 队列管理与角色协调

#### queue-manager Skill 职责

| 职责 | 说明 |
|------|------|
| 队列状态检查 | 读取 queue.json 统计任务数量 |
| 阈值控制 | 任务 > 10 时暂停分配，≤ 5 时恢复 |
| 角色通知 | 向相关角色发送队列状态通知 |
| 任务优先级 | 高优先级任务可突破阈值限制 |

#### 协调流程

```
1. Coach 想安排新任务给 CEO
   ↓
2. 调用 queue-manager 检查队列状态
   ↓
3. queue-manager 读取 queue.json 统计数量
   ↓
4. 返回状态：
   - 队列 ≤ 10 → 允许安排
   - 队列 > 10 → 拒绝安排，记录等待
   ↓
5. 队列恢复后通知 Coach 继续安排
```

---

## 6. 运维管理

### 6.1 查看任务状态

```bash
# 查看待执行任务
type E:\workspaces_2026_python\claude_code_cookbook\claude-code-24h-integration\tasks\queue.json

# 查看已完成任务
type E:\workspaces_2026_python\claude_code_cookbook\claude-code-24h-integration\tasks\completed.json

# 查看失败任务
type E:\workspaces_2026_python\claude_code_cookbook\claude-code-24h-integration\tasks\failed.json

# 查看运行中任务
type E:\workspaces_2026_python\claude_code_cookbook\claude-code-24h-integration\tasks\running.json
```

### 6.2 查看日志

```bash
# PM2 日志
pm2 logs claude-runner

# 日志文件位置
E:\workspaces_2026_python\claude_code_cookbook\claude-code-24h-integration\logs\runner-out.log
E:\workspaces_2026_python\claude_code_cookbook\claude-code-24h-integration\logs\runner-error.log
```

### 6.3 手动添加任务

```bash
cd E:\workspaces_2026_python\claude_code_cookbook\claude-code-24h-integration

# 使用批处理脚本
scripts\add-task.bat "你的任务描述"

# 使用 Node.js
node src/add-task.js "你的任务描述" --workspace "E:\workspaces_2026_python\OPC-CEO" --auto-approve
```

### 6.4 清空任务队列

```bash
echo {"list":[]} > E:\workspaces_2026_python\claude_code_cookbook\claude-code-24h-integration\tasks\queue.json
```

---

## 7. 定时任务配置

### 7.1 Cron 表达式格式

| 格式 | 说明 |
|------|------|
| `0 * * * *` | 每小时整点 |
| `*/30 * * * *` | 每 30 分钟 |
| `0 9 * * *` | 每天 9:00 |
| `0 9,12,18 * * *` | 每天 9:00, 12:00, 18:00 |
| `0 9 * * 1-5` | 周一到周五 9:00 |

### 7.2 启用/禁用定时任务

编辑 `scheduled.json`，设置 `enabled` 字段：

```json
{
  "id": "opc-coach-planning",
  "enabled": true   // true=启用, false=禁用
}
```

---

## 8. 队列管理 Skill 使用

### 8.1 激活 queue-manager

```
你是 queue-manager。任务：检查当前任务队列状态...
```

### 8.2 检查队列状态

```
检查 queue.json 中的任务数量，判断是否允许安排新任务。
```

### 8.3 阈值控制规则

| 条件 | 动作 |
|------|------|
| 队列任务数 > 10 | 暂停安排，返回"队列已满，请稍后再试" |
| 队列任务数 ≤ 5 | 恢复安排，通知相关角色 |
| 5 < 队列任务数 ≤ 10 | 正常安排，但提示队列较忙 |

---

## 9. 故障排查

| 问题 | 检查方法 | 解决方案 |
|------|----------|----------|
| PM2 进程离线 | `pm2 status` | `pm2 restart claude-runner` |
| 任务卡住不执行 | 检查 running.json | `del running.json` |
| 队列任务不执行 | 检查 scheduled.json | 检查 enabled 字段 |
| 内存持续增长 | `pm2 monit` | 等待 cron_restart 或手动重启 |

---

## 10. 快速参考

### 10.1 PM2 命令速查

```bash
pm2 start ecosystem.config.js    # 启动
pm2 status                       # 状态
pm2 logs claude-runner           # 日志
pm2 restart claude-runner        # 重启
pm2 stop claude-runner           # 停止
pm2 save                         # 保存状态
```

### 10.2 队列管理

| 文件 | 位置 | 用途 |
|------|------|------|
| queue.json | tasks/queue.json | 待执行任务 |
| completed.json | tasks/completed.json | 已完成任务 |
| failed.json | tasks/failed.json | 失败任务 |
| scheduled.json | tasks/scheduled.json | 定时任务配置 |

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v2.0 | 2026-02-26 | 更新为 claude-code-24h-integration，简化 PM2 流程，新增队列管理 Skill |
| v1.0 | 2026-02-25 | 初始版本 |
