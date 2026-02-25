# 删除 opc-coach-planning 定时任务

$taskName = "OPCCoachPlanning"

Unregister-ScheduledTask -TaskName $taskName -Confirm:$false

Write-Host "任务已删除: $taskName" -ForegroundColor Green
