#!/usr/bin/env python3
"""
跨会话状态持久化脚本

功能：
- 保存当前会话状态到文件
- 下次会话启动时恢复状态
- 记录会话间的上下文

使用 uv 运行:
    uv run state_persistence.py save     # 保存当前状态
    uv run state_persistence.py load      # 加载上次状态
    uv run state_persistence.py clear     # 清除状态

状态存储位置: .claude/skills/ceo-coach/scripts/.session_state.json
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
STATE_FILE = PROJECT_ROOT / ".claude" / "skills" / "ceo-coach" / "scripts" / ".session_state.json"


# 状态版本
STATE_VERSION = "1.0.0"


class SessionState:
    """会话状态管理器"""

    def __init__(self):
        self.state: dict[str, Any] = {
            "version": STATE_VERSION,
            "current_session": None,
            "previous_session": None,
            "context": {},
            "last_task": None,
            "pending_tasks": [],
            "completed_tasks": [],
            "last_action": None,
            "memory_snapshot": None,
            "created_at": None,
            "updated_at": None
        }

    def load(self) -> dict[str, Any]:
        """加载状态文件"""
        if STATE_FILE.exists():
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                self.state = json.load(f)
        return self.state

    def save(self) -> None:
        """保存状态文件"""
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.state["updated_at"] = datetime.now().isoformat()

        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def update_context(self, key: str, value: Any) -> None:
        """更新上下文"""
        self.state["context"][key] = value
        self.state["updated_at"] = datetime.now().isoformat()

    def set_current_session(self, session_id: str) -> None:
        """设置当前会话 ID"""
        previous = self.state.get("current_session")
        self.state["previous_session"] = previous
        self.state["current_session"] = session_id
        if not self.state.get("created_at"):
            self.state["created_at"] = datetime.now().isoformat()
        self.state["updated_at"] = datetime.now().isoformat()

    def add_pending_task(self, task_id: str, description: str) -> None:
        """添加待办任务"""
        task = {
            "id": task_id,
            "description": description,
            "added_at": datetime.now().isoformat()
        }
        self.state["pending_tasks"].append(task)
        self.state["updated_at"] = datetime.now().isoformat()

    def complete_task(self, task_id: str) -> None:
        """标记任务完成"""
        pending = self.state.get("pending_tasks", [])
        completed = self.state.get("completed_tasks", [])

        for task in pending:
            if task.get("id") == task_id:
                pending.remove(task)
                task["completed_at"] = datetime.now().isoformat()
                completed.append(task)
                break

        self.state["pending_tasks"] = pending
        self.state["completed_tasks"] = completed
        self.state["updated_at"] = datetime.now().isoformat()

    def set_memory_snapshot(self, snapshot: dict[str, Any]) -> None:
        """设置 Memory 快照"""
        self.state["memory_snapshot"] = snapshot
        self.state["updated_at"] = datetime.now().isoformat()

    def get_memory_snapshot(self) -> Optional[dict[str, Any]]:
        """获取 Memory 快照"""
        return self.state.get("memory_snapshot")

    def get_context(self, key: str, default: Any = None) -> Any:
        """获取上下文值"""
        return self.state.get("context", {}).get(key, default)

    def clear(self) -> None:
        """清除状态"""
        self.state = {
            "version": STATE_VERSION,
            "current_session": None,
            "previous_session": None,
            "context": {},
            "last_task": None,
            "pending_tasks": [],
            "completed_tasks": [],
            "last_action": None,
            "memory_snapshot": None,
            "created_at": None,
            "updated_at": datetime.now().isoformat()
        }


def save_state(session_id: Optional[str] = None) -> dict[str, Any]:
    """保存当前状态"""
    print("=" * 50)
    print("保存会话状态")
    print("=" * 50)

    state_mgr = SessionState()
    state_mgr.load()

    if session_id:
        state_mgr.set_current_session(session_id)
        print(f"当前会话: {session_id}")

    state_mgr.save()

    print(f"状态已保存到: {STATE_FILE}")
    print(f"待办任务数: {len(state_mgr.state.get('pending_tasks', []))}")
    print(f"已完成任务数: {len(state_mgr.state.get('completed_tasks', []))}")

    return {
        "success": True,
        "state_file": str(STATE_FILE),
        "session_id": state_mgr.state.get("current_session")
    }


def load_state() -> dict[str, Any]:
    """加载上次状态"""
    print("=" * 50)
    print("加载会话状态")
    print("=" * 50)

    if not STATE_FILE.exists():
        print("没有找到状态文件")
        return {
            "success": False,
            "error": "No state file found",
            "has_state": False
        }

    state_mgr = SessionState()
    state_mgr.load()

    print(f"当前会话: {state_mgr.state.get('current_session')}")
    print(f"上次会话: {state_mgr.state.get('previous_session')}")
    print(f"待办任务数: {len(state_mgr.state.get('pending_tasks', []))}")
    print(f"已完成任务数: {len(state_mgr.state.get('completed_tasks', []))}")

    # 显示上下文
    context = state_mgr.state.get("context", {})
    if context:
        print("\n上下文:")
        for key, value in context.items():
            print(f"  - {key}: {value}")

    return {
        "success": True,
        "has_state": True,
        "current_session": state_mgr.state.get("current_session"),
        "previous_session": state_mgr.state.get("previous_session"),
        "pending_tasks": state_mgr.state.get("pending_tasks", []),
        "completed_tasks": state_mgr.state.get("completed_tasks", []),
        "context": state_mgr.state.get("context", {}),
        "created_at": state_mgr.state.get("created_at"),
        "updated_at": state_mgr.state.get("updated_at")
    }


def clear_state() -> dict[str, Any]:
    """清除状态"""
    print("=" * 50)
    print("清除会话状态")
    print("=" * 50)

    state_mgr = SessionState()
    state_mgr.clear()
    state_mgr.save()

    print("状态已清除")

    return {
        "success": True,
        "message": "State cleared"
    }


def update_context(key: str, value: Any) -> dict[str, Any]:
    """更新上下文"""
    state_mgr = SessionState()
    state_mgr.load()
    state_mgr.update_context(key, value)
    state_mgr.save()

    print(f"上下文已更新: {key} = {value}")

    return {
        "success": True,
        "key": key,
        "value": value
    }


def print_json(data: Any) -> None:
    """打印 JSON 输出"""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main() -> None:
    """CLI 入口"""
    if len(sys.argv) < 2:
        print("跨会话状态持久化工具")
        print("")
        print("用法:")
        print("  uv run state_persistence.py save [session_id]  # 保存状态")
        print("  uv run state_persistence.py load               # 加载状态")
        print("  uv run state_persistence.py clear               # 清除状态")
        print("  uv run state_persistence.py set <key> <value>   # 设置上下文")
        print("  uv run state_persistence.py get <key>           # 获取上下文")
        print("")
        print(f"状态文件: {STATE_FILE}")
        sys.exit(1)

    command = sys.argv[1]

    if command == "save":
        session_id = sys.argv[2] if len(sys.argv) > 2 else None
        result = save_state(session_id)
        print_json(result)

    elif command == "load":
        result = load_state()
        print_json(result)

    elif command == "clear":
        result = clear_state()
        print_json(result)

    elif command == "set":
        if len(sys.argv) < 4:
            print("用法: uv run state_persistence.py set <key> <value>")
            sys.exit(1)
        key = sys.argv[2]
        value = sys.argv[3]
        result = update_context(key, value)
        print_json(result)

    elif command == "get":
        if len(sys.argv) < 3:
            print("用法: uv run state_persistence.py get <key>")
            sys.exit(1)
        key = sys.argv[2]
        state_mgr = SessionState()
        state_mgr.load()
        value = state_mgr.get_context(key)
        print_json({"key": key, "value": value})

    else:
        print_json({"error": f"未知命令: {command}"})
        sys.exit(1)


if __name__ == "__main__":
    main()
