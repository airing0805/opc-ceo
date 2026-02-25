# Register opc-coach-planning scheduled task
# Runs every 20 minutes

$taskName = "OPCCoachPlanning"
$scriptPath = "E:\workspaces_2026_python\OPC-CEO\.claude\schedules\opc-coach-planning.bat"
$description = "Coach self-evolution planning task - Run every 20 minutes"

# Remove existing task if any
Unregister-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue -Confirm:$false

$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `'$scriptPath`'"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 20)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description $description -Force

Write-Host "Task registered: $taskName" -ForegroundColor Green
Write-Host "Script: $scriptPath" -ForegroundColor Cyan
Write-Host "Frequency: Every 20 minutes" -ForegroundColor Cyan
Write-Host ""
Write-Host "View task: Get-ScheduledTaskInfo -TaskName $taskName" -ForegroundColor Yellow
Write-Host "Run manually: Start-ScheduledTask -TaskName $taskName" -ForegroundColor Yellow
Write-Host "Delete task: Unregister-ScheduledTask -TaskName $taskName" -ForegroundColor Yellow
