# 删除 coach-self-evolution 定时任务

$taskName = "CoachSelfEvolution"

Unregister-ScheduledTask -TaskName $taskName -Confirm:$false

Write-Host "Task deleted: $taskName" -ForegroundColor Green
