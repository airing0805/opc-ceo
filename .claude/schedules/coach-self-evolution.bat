@echo off
chcp 65001 > nul
set PROJECT_DIR=E:\workspaces_2026_python\OPC-CEO
set LOG_DIR=%PROJECT_DIR%\.claude\logs
set LOG_FILE=%LOG_DIR%\coach-self-evolution.log
set ERROR_FILE=%LOG_DIR%\coach-self-evolution.error.log

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

cd /d "%PROJECT_DIR%"

echo [%date% %time%] Starting coach-self-evolution task... >> "%LOG_FILE%"
claude -p "你是 ceo-coach。任务：先进行自我进化，优化自身的能力。分析当前项目需要优化和改进的内容，生成需要执行的任务。任务必须有价值，任务价值 = 战略对齐度 × 紧急程度 × 实现可行性" --dangerously-skip-permissions >> "%LOG_FILE%" 2>> "%ERROR_FILE%"
echo [%date% %time%] Task completed. >> "%LOG_FILE%"
