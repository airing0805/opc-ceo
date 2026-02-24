#!/usr/bin/env python3
"""
Claude Code SDK 会话管理器

功能：
- 列出 Claude Code 历史会话
- 获取会话详情
- 恢复会话执行任务
- 删除会话

会话存储位置: ~/.claude/projects/<project_hash>/<session_id>.jsonl
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Optional

# Claude Code 会话存储目录
CLAUDE_DIR = Path.home() / ".claude"
PROJECTS_DIR = CLAUDE_DIR / "projects"


def get_project_hash(project_path: str) -> str:
    """根据项目路径生成哈希值（与 Claude Code 一致）"""
    abs_path = Path(project_path).resolve()
    path_str = str(abs_path).replace("\\", "/")
    return hashlib.md5(path_str.encode()).hexdigest()[:16]


def get_path_based_dirname(project_path: str) -> str:
    """根据项目路径生成目录名（路径替换方式）"""
    abs_path = Path(project_path).resolve()
    path_str = str(abs_path)
    # 替换特殊字符为 -
    result = path_str.replace(":", "-").replace("\\", "-").replace("/", "-").replace("_", "-")
    # Windows 盘符小写（如 E- 变成 e-）
    if len(result) >= 2 and result[1] == "-":
        result = result[0].lower() + result[1:]
    return result


def get_sessions_dir(working_dir: str) -> Path | None:
    """获取指定项目的会话目录（支持两种命名方式）"""
    # 优先方式2：路径替换（因为 Claude Code 实际使用这种方式）
    path_dirname = get_path_based_dirname(working_dir)
    path_dir = PROJECTS_DIR / path_dirname
    if path_dir.exists():
        return path_dir

    # 方式1：MD5 hash（作为备用）
    project_hash = get_project_hash(working_dir)
    hash_dir = PROJECTS_DIR / project_hash
    if hash_dir.exists():
        return hash_dir

    # 都不存在，返回路径替换目录（与 Claude Code 一致）
    return path_dir


def parse_session_metadata(filepath: Path) -> dict[str, Any]:
    """解析会话文件获取元数据"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            first_user_msg = None
            timestamp = None
            session_id = None
            message_count = 0
            tools_used: set[str] = set()
            cwd = None

            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    msg_type = data.get("type")

                    if msg_type == "user":
                        # 提取 cwd（工作目录）
                        if cwd is None:
                            cwd = data.get("cwd")

                        if not first_user_msg:
                            content = data.get("message", {}).get("content", [])
                            # 处理 content 为字符串的情况
                            if isinstance(content, str):
                                text = content
                                if "<ide_selection>" not in text and "<ide_opened_file>" not in text:
                                    first_user_msg = text[:100] + ("..." if len(text) > 100 else "")
                            # 处理 content 为数组的情况
                            elif content and isinstance(content, list):
                                for item in content:
                                    if item.get("type") == "text":
                                        text = item.get("text", "")
                                        if "<ide_selection>" not in text and "<ide_opened_file>" not in text:
                                            first_user_msg = text[:100] + ("..." if len(text) > 100 else "")
                                            break
                            timestamp = data.get("timestamp")
                            session_id = data.get("sessionId")
                        message_count += 1
                    elif msg_type == "assistant":
                        message_count += 1
                        # 提取工具使用信息
                        content = data.get("message", {}).get("content", [])
                        if content and isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict) and item.get("type") == "tool_use":
                                    tool_name = item.get("name", "")
                                    if tool_name:
                                        tools_used.add(tool_name)
                except json.JSONDecodeError:
                    continue

        return {
            "id": session_id or filepath.stem,
            "title": first_user_msg or "无标题",
            "timestamp": timestamp,
            "message_count": message_count,
            "size": filepath.stat().st_size if filepath.exists() else 0,
            "tools": sorted(list(tools_used)),
            "cwd": cwd,
        }
    except Exception as e:
        return {
            "id": filepath.stem,
            "title": f"解析错误: {str(e)[:30]}",
            "timestamp": None,
            "message_count": 0,
            "size": 0,
            "tools": [],
            "cwd": None,
        }


def find_session_file(session_id: str) -> Optional[Path]:
    """在所有项目中查找会话文件"""
    if not PROJECTS_DIR.exists():
        return None

    for project_dir in PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue
        # 尝试直接匹配文件名
        session_file = project_dir / f"{session_id}.jsonl"
        if session_file.exists():
            return session_file
        # 尝试匹配以 session_id 开头的文件
        for filepath in project_dir.glob("*.jsonl"):
            if filepath.stem.startswith(session_id[:8]):
                return filepath
    return None


def list_sessions(working_dir: str) -> list[dict[str, Any]]:
    """列出指定项目的会话"""
    sessions_dir = get_sessions_dir(working_dir)

    if not sessions_dir.exists():
        return []

    sessions = []
    for filepath in sessions_dir.glob("*.jsonl"):
        metadata = parse_session_metadata(filepath)
        sessions.append(metadata)

    # 按时间戳降序排序
    sessions.sort(key=lambda x: x.get("timestamp") or "", reverse=True)
    return sessions


def list_all_projects() -> list[dict[str, Any]]:
    """列出所有项目"""
    if not PROJECTS_DIR.exists():
        return []

    projects = []
    for project_dir in PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue

        session_files = list(project_dir.glob("*.jsonl"))
        session_count = len(session_files)

        # 获取第一个会话的工作目录
        real_path: str | None = None
        for session_file in session_files:
            metadata = parse_session_metadata(session_file)
            if metadata.get("cwd"):
                real_path = metadata.get("cwd")
                break

        projects.append({
            "hash": project_dir.name,
            "path": real_path or project_dir.name,
            "session_count": session_count,
        })

    # 按会话数量降序排序
    projects.sort(key=lambda x: x["session_count"], reverse=True)
    return projects


def get_session_detail(session_id: str) -> Optional[dict[str, Any]]:
    """获取会话详情"""
    session_file = find_session_file(session_id)
    if not session_file:
        return None

    metadata = parse_session_metadata(session_file)
    metadata["file_path"] = str(session_file)
    return metadata


def delete_session(session_id: str) -> bool:
    """删除会话文件"""
    session_file = find_session_file(session_id)
    if session_file and session_file.exists():
        session_file.unlink()
        return True
    return False


async def execute_task(
    prompt: str,
    session_id: Optional[str] = None,
    allowed_tools: Optional[list[str]] = None,
    cwd: Optional[str] = None,
    system_prompt: Optional[str] = None,
    max_turns: int = 10,
) -> dict[str, Any]:
    """
    执行任务（使用 SDK，会话自动保存到 ~/.claude/projects/）

    Args:
        prompt: 任务提示
        session_id: 要恢复的会话 ID（可选）
        allowed_tools: 允许使用的工具列表
        cwd: 工作目录
        system_prompt: 系统提示
        max_turns: 最大轮次

    Returns:
        执行结果字典
    """
    try:
        from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, ResultMessage, AssistantMessage
    except ImportError:
        return {
            "success": False,
            "error": "claude-agent-sdk 未安装，请运行: uv sync",
            "session_id": None,
        }

    options = ClaudeAgentOptions(
        permission_mode="acceptEdits",
        cwd=cwd or ".",
        continue_conversation=(session_id is not None),
        max_turns=10,
        max_budget_usd=100,
    )

    result_text: Optional[str] = None
    new_session_id: Optional[str] = session_id
    turns = 0
    cost_usd = 0.0

    try:
        async with ClaudeSDKClient(options=options) as client:
            await client.query(prompt, session_id=session_id or "default")

            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if hasattr(block, "text") and block.text:
                            result_text = (result_text or "") + block.text
                elif isinstance(message, ResultMessage):
                    new_session_id = getattr(message, "session_id", None)
                    cost_usd = message.total_cost_usd or 0.0
                    turns = getattr(message, "turns", 0)

        return {
            "success": True,
            "session_id": new_session_id,
            "result": result_text,
            "turns": turns,
            "cost_usd": cost_usd,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "session_id": new_session_id,
        }
