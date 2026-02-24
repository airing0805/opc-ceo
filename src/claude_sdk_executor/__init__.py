"""
Claude SDK 执行器 - 通过 Bash 执行 Python 脚本，使用 claude-agent-sdk 调用 Claude Code API
"""

__version__ = "3.1.0"

from .sessions import (
    list_sessions,
    list_all_projects,
    get_session_detail,
    delete_session,
    execute_task,
)

__all__ = [
    "__version__",
    "list_sessions",
    "list_all_projects",
    "get_session_detail",
    "delete_session",
    "execute_task",
]
