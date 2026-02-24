# 查看 coach-self-evolution 任务日志

$logDir = "E:\workspaces_2026_python\OPC-CEO\.claude\logs"
$logFile = "$logDir\coach-self-evolution.log"
$errorFile = "$logDir\coach-self-evolution.error.log"

Write-Host "=== Log File ===" -ForegroundColor Cyan
if (Test-Path $logFile) {
    Get-Content $logFile -Tail 50
} else {
    Write-Host "Log file not found: $logFile" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Error Log ===" -ForegroundColor Cyan
if (Test-Path $errorFile) {
    $errorContent = Get-Content $errorFile -Tail 20
    if ($errorContent) {
        Write-Host $errorContent -ForegroundColor Red
    } else {
        Write-Host "No errors logged." -ForegroundColor Green
    }
} else {
    Write-Host "Error log file not found: $errorFile" -ForegroundColor Yellow
}
