@echo off
chcp 65001 > nul
set PROJECT_DIR=E:\workspaces_2026_python\OPC-CEO
set LOG_DIR=%PROJECT_DIR%\.claude\logs\evolution
set LOG_FILE=%LOG_DIR%\evolution-%date:~0,4%%date:~5,2%%date:~8,2%.log
set ERROR_FILE=%LOG_DIR%\evolution-error.log

REM Set Node.js environment for SYSTEM account
set NODE_PATH=E:\tools\nodejsnvm
set PATH=%NODE_PATH%;%PATH%
set CLAUDE_PATH=%NODE_PATH%\claude.cmd

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

cd /d "%PROJECT_DIR%"

echo ======================================== >> "%LOG_FILE%"
echo [%date% %time%] Starting daily evolution task... >> "%LOG_FILE%"
echo Working directory: %CD% >> "%LOG_FILE%"
echo User: %USERNAME% >> "%LOG_FILE%"

REM Execute 24h self-evolution check
REM The prompt includes:
REM 1. Check Memory status
REM 2. Check Git status
REM 3. Check uncompleted tasks
REM 4. Generate evolution report

set CLAUDECODE=
call "%CLAUDE_PATH%" -p "你是 ceo-coach。执行 24h 自我进化流程：

## 1. 系统状态检查

### Memory 状态检查
- 使用 mcp__memory__search_nodes 搜索 'company status task project'
- 如果 Memory 为空，从以下文档读取并重建：
  - docs/沟通文档/任务分配.md -> Task 实体
  - docs/战略规划/战略目标.md -> Goal 实体
  - docs/版本规划/v2-技能规划/README.md -> Progress 实体

### Git 状态检查
- 运行 git status 检查未提交的变更
- 运行 git log --oneline -5 检查最近的提交
- 如果有变更，记录到进化报告

### 待办任务检查
- 读取 docs/沟通文档/任务分配.md
- 统计各状态任务数量（待执行/进行中/已完成/阻塞）
- 识别阻塞任务和逾期任务

## 2. 生成进化报告

创建/更新进化日志文件：.claude/logs/evolution/evolution-report.md

报告格式：
# Coach 24h 进化报告

**生成时间**: YYYY-MM-DD HH:MM
**报告周期**: 过去24小时

## 系统状态摘要

| 检查项 | 状态 | 说明 |
|--------|------|------|
| Memory | 状态描述 | 实体数量/空白/已恢复 |
| Git | 状态描述 | 变更数量/分支状态 |
| 待办任务 | 状态描述 | 待执行/已完成/阻塞数量 |

## 任务执行进度

### 已完成任务
- 列出过去24小时完成的任务

### 进行中任务
- 列出当前正在执行的任务

### 阻塞任务
- 列出被阻塞的任务及原因

## 进化建议

1. 针对发现的问题提出改进建议
2. 针对阻塞任务提出解决方案
3. 识别新的优化机会

## 下一步行动

- 列出今日优先任务

## 进化指标

| 指标 | 昨日值 | 今日值 | 变化 |
|------|--------|--------|------|
| 任务完成率 | X% | Y% | +/-Z% |
| 阻塞任务数 | X | Y | +/-Z |
| Memory实体数 | X | Y | +/-Z |

## 3. 执行优化

根据检查结果，执行以下优化（如果需要）：
- 如果 Memory 为空，从文档重建实体
- 如果有阻塞任务，尝试解决或记录原因
- 如果发现新任务机会，生成任务并记录到任务分配.md

不要和用户沟通，直接执行并记录结果。" --dangerously-skip-permissions >> "%LOG_FILE%" 2>> "%ERROR_FILE%"

echo [%date% %time%] Evolution task completed. Exit code: %ERRORLEVEL% >> "%LOG_FILE%"
