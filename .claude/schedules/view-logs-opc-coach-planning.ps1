# 查看 opc-coach-planning 任务日志

$logDir = "E:\workspaces_2026_python\OPC-CEO\.claude\logs"
$logFile = "$logDir\opc-coach-planning.log"
$errorFile = "$logDir\opc-coach-planning.error.log"

Write-Host "=== 日志文件 ===" -ForegroundColor Cyan
if (Test-Path $logFile) {
    Get-Content $logFile -Tail 50
} else {
    Write-Host "日志文件不存在: $logFile" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== 错误日志 ===" -ForegroundColor Cyan
if (Test-Path $errorFile) {
    $errorContent = Get-Content $errorFile -Tail 20
    if ($errorContent) {
        Write-Host $errorContent -ForegroundColor Red
    } else {
        Write-Host "无错误记录" -ForegroundColor Green
    }
} else {
    Write-Host "错误日志文件不存在: $errorFile" -ForegroundColor Yellow
}
