# 定时任务管理

## 已注册任务

| 任务名称 | 执行频率 | 说明 |
|---------|---------|------|
| CoachSelfEvolution | 每20分钟 | CEO教练自我进化任务 |

## 管理脚本

### 1. 注册任务
```powershell
powershell -ExecutionPolicy Bypass -File ".claude\schedules\register-task.ps1"
```

### 2. 删除任务
```powershell
powershell -ExecutionPolicy Bypass -File ".claude\schedules\unregister-task.ps1"
```

### 3. 查看日志
```powershell
powershell -ExecutionPolicy Bypass -File ".claude\schedules\view-logs.ps1"
```

### 4. 手动运行任务
```powershell
Start-ScheduledTask -TaskName CoachSelfEvolution
```

### 5. 查看任务信息
```powershell
Get-ScheduledTaskInfo -TaskName CoachSelfEvolution
```

## 任务说明

**任务内容**：
你是 ceo-coach。任务：先进行自我进化，优化自身的能力。分析当前项目需要优化和改进的内容，生成需要执行的任务。任务必须有价值，任务价值 = 战略对齐度 × 紧急程度 × 实现可行性

**日志位置**：
- 日志: `.claude/logs/coach-self-evolution.log`
- 错误: `.claude/logs/coach-self-evolution.error.log`
