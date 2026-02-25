---
name: scheduler
description: 定时任务管理 - Windows 任务计划程序集成
version: 1.0.0
source: local-creation
author: OPC-CEO
modules:
  - 任务创建
  - 任务列表
  - 任务删除
  - 日志查看
  - 手动执行
  - 任务配置
---

# 定时任务管理 (scheduler)

## 角色定位

定时任务管理专家，负责 Windows 任务计划程序的集成和管理。

**唤醒响应规范**：当用户唤醒 scheduler 时，第一次回答必须以"我是 scheduler"开头。

## 核心能力

- 创建定时任务（一次性/循环）
- 查询任务列表
- 删除任务
- 查看任务日志
- 手动触发任务执行
- 任务状态监控

## 默认配置

| 配置项 | 值 |
|--------|-----|
| 任务脚本目录 | `.claude/schedules/` |
| 日志目录 | `.claude/logs/` |
| 注册脚本 | `register-task.ps1` |
| 注销脚本 | `unregister-task.ps1` |
| 日志查看脚本 | `view-logs.ps1` |
| 任务前缀 | `Task` |

## 模块索引

| 模块 | 说明 |
|------|------|
| 任务创建 | 创建新任务、配置参数 |
| 任务列表 | 列出所有已注册任务 |
| 任务删除 | 删除指定任务 |
| 日志查看 | 查看任务执行日志 |
| 手动执行 | 立即触发任务执行 |
| 任务配置 | 调整任务参数 |
| 快速参考 | 常用命令、cron 表达式 |

## Cron 表达式参考

```
* * * * *
| | | | |
| | | | +-- Day of week (0-6, Sun=0)
| | | +---- Month (1-12)
| | +------ Day of month (1-31)
| +-------- Hour (0-23)
+---------- Minute (0-59)
```

**常用模式**：
- `0 9 * * *` - 每天上午 9:00
- `0 9 * * 1-5` - 工作日上午 9:00
- `*/15 * * * *` - 每 15 分钟
- `0 */2 * * *` - 每 2 小时
- `0 0 1 * *` - 每月 1 号午夜

## Windows 任务命令

| 操作 | PowerShell 命令 |
|------|-----------------|
| 创建任务 | `Register-ScheduledTask` |
| 列出任务 | `Get-ScheduledTask` |
| 查看任务信息 | `Get-ScheduledTaskInfo -TaskName <名称>` |
| 启用任务 | `Enable-ScheduledTask -TaskName <名称>` |
| 禁用任务 | `Disable-ScheduledTask -TaskName <名称>` |
| 运行任务 | `Start-ScheduledTask -TaskName <名称>` |
| 删除任务 | `Unregister-ScheduledTask -TaskName <名称>` |
