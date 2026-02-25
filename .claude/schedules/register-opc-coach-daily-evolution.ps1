# Register opc-coach-daily-evolution scheduled task
# Runs daily at 08:00 for 24h self-evolution check

$taskName = "OPCCoachDailyEvolution"
$scriptPath = "E:\workspaces_2026_python\OPC-CEO\.claude\schedules\opc-coach-daily-evolution.bat"
$workingDir = "E:\workspaces_2026_python\OPC-CEO"
$description = "Coach 24h self-evolution task - Run daily at 08:00"

# Remove existing task if any
Unregister-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue -Confirm:$false

# Execute bat file directly (not via cmd /c) for SYSTEM account compatibility
$action = New-ScheduledTaskAction -Execute $scriptPath -WorkingDirectory $workingDir

# Daily trigger at 08:00
$trigger = New-ScheduledTaskTrigger -Daily -At "08:00"

$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

# Use SYSTEM account for background execution (runs without interactive session)
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description $description -Force

Write-Host "Daily evolution task registered: $taskName" -ForegroundColor Green
Write-Host "Script: $scriptPath" -ForegroundColor Cyan
Write-Host "Frequency: Daily at 08:00" -ForegroundColor Cyan
Write-Host ""
Write-Host "View task: Get-ScheduledTaskInfo -TaskName $taskName" -ForegroundColor Yellow
Write-Host "Run manually: Start-ScheduledTask -TaskName $taskName" -ForegroundColor Yellow
Write-Host "Delete task: Unregister-ScheduledTask -TaskName $taskName" -ForegroundColor Yellow
