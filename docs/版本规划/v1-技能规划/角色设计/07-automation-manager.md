# 自动化专家 (automation-manager)

## 角色定位

工作流自动化与定时任务

## 能力要求

- 定时任务定义（Cron 表达式）
- 工作流设计（顺序、并行、条件）
- 触发器配置（时间、事件）
- 任务执行（调用其他技能）
- 执行日志

## 技能文件

| 文件 | 职责 |
|------|------|
| `SKILL.md` | 主入口 - 与 scheduler skill 集成 |
| `工作流定义.md` | 工作流定义格式 |
| `触发器.md` | 触发器配置（定时/事件） |
| `执行器.md` | 执行逻辑、错误重试 |

## 工作流定义

```yaml
workflow:
  id: daily-review
  name: 每日回顾
  trigger:
    type: cron
    schedule: "0 18 * * *"  # 每天 18:00
  steps:
    - name: 收集完成的任务
      skill: task-manager
      action: get-completed-today
    - name: 生成日报
      skill: task-manager
      action: generate-daily-report
    - name: 保存报告
      skill: file-manager
      action: save-file
```

## 与 scheduler skill 的集成

automation-manager 通过 scheduler skill 实现定时任务：
- 定义工作流
- 配置触发器
- 调用其他技能执行具体任务

## 教练角色

参见：[教练-automation-manager](./教练-07-automation-manager.md)
