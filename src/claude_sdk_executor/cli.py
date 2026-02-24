"""CLI 入口模块"""

import asyncio
import json
import sys
from pathlib import Path

from .sessions import (
    list_sessions,
    list_all_projects,
    get_session_detail,
    delete_session,
    execute_task,
)


def print_json(data: object) -> None:
    """打印 JSON 输出（支持 Windows GBK 编码）"""
    output = json.dumps(data, ensure_ascii=False, indent=2)
    if sys.platform == "win32":
        sys.stdout.buffer.write(output.encode("utf-8"))
        sys.stdout.buffer.write(b"\n")
    else:
        print(output)


def main() -> None:
    """CLI 入口"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  claude-executor list --cwd <path>       # 列出项目的会话")
        print("  claude-executor projects                # 列出所有项目")
        print("  claude-executor get <session_id>        # 获取会话详情")
        print("  claude-executor delete <session_id>     # 删除会话")
        print("  claude-executor exec <prompt> [options] # 执行任务")
        print("")
        print("选项:")
        print("  --cwd <path>           工作目录")
        print("  --resume <session_id>  恢复指定会话")
        print("  --tools <tool1,tool2>  允许的工具")
        print("")
        print("会话存储位置: ~/.claude/projects/<project_hash>/<session_id>.jsonl")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        cwd = str(Path.cwd())
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--cwd" and i + 1 < len(sys.argv):
                cwd = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        sessions = list_sessions(cwd)
        print_json({"sessions": sessions, "count": len(sessions), "cwd": cwd})

    elif command == "projects":
        projects = list_all_projects()
        print_json({"projects": projects, "count": len(projects)})

    elif command == "get":
        if len(sys.argv) < 3:
            print_json({"error": "需要提供 session_id"})
            sys.exit(1)
        session = get_session_detail(sys.argv[2])
        if session:
            print_json(session)
        else:
            print_json({"error": "会话不存在"})

    elif command == "delete":
        if len(sys.argv) < 3:
            print_json({"error": "需要提供 session_id"})
            sys.exit(1)
        deleted = delete_session(sys.argv[2])
        print_json({"deleted": deleted})

    elif command == "exec":
        if len(sys.argv) < 3:
            print_json({"error": "需要提供 prompt"})
            sys.exit(1)

        prompt = sys.argv[2]
        session_id: str | None = None
        cwd: str | None = str(Path.cwd())
        tools = ["Read", "Glob", "Grep", "Bash"]

        # 解析选项
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--resume" and i + 1 < len(sys.argv):
                session_id = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--cwd" and i + 1 < len(sys.argv):
                cwd = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--tools" and i + 1 < len(sys.argv):
                tools = sys.argv[i + 1].split(",")
                i += 2
            else:
                i += 1

        result = asyncio.run(
            execute_task(
                prompt=prompt,
                session_id=session_id,
                allowed_tools=tools,
                cwd=cwd,
            )
        )
        print_json(result)

    else:
        print_json({"error": f"未知命令: {command}"})
        sys.exit(1)
