# Register opc-coach-planning scheduled task
# Runs every 20 minutes

$taskName = "OPCCoachPlanning"
$scriptPath = "E:\workspaces_2026_python\OPC-CEO\.claude\schedules\opc-coach-planning.bat"
$workingDir = "E:\workspaces_2026_python\OPC-CEO"
$description = "Coach self-evolution planning task - Run every 20 minutes"

# Remove existing task if any
Unregister-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue -Confirm:$false

# Execute bat file directly (not via cmd /c) for SYSTEM account compatibility
$action = New-ScheduledTaskAction -Execute $scriptPath -WorkingDirectory $workingDir
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 20)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

# Use SYSTEM account for background execution (runs without interactive session)
# NOTE: SYSTEM account cannot access user's Claude login state - needs API Key
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description $description -Force

Write-Host "Task registered: $taskName" -ForegroundColor Green
Write-Host "Script: $scriptPath" -ForegroundColor Cyan
Write-Host "Frequency: Every 20 minutes" -ForegroundColor Cyan
Write-Host ""
Write-Host "View task: Get-ScheduledTaskInfo -TaskName $taskName" -ForegroundColor Yellow
Write-Host "Run manually: Start-ScheduledTask -TaskName $taskName" -ForegroundColor Yellow
Write-Host "Delete task: Unregister-ScheduledTask -TaskName $taskName" -ForegroundColor Yellow
