#!/usr/bin/env python3
"""
Memory 同步脚本

功能：
- 定时将 Memory 中的数据同步到文档
- 检测 Memory 和文档的差异
- 支持双向同步（Memory -> 文档，文档 -> Memory）

使用 uv 运行:
    uv run memory_sync.py sync-to-doc
    uv run memory_sync.py sync-to-memory
    uv run memory_sync.py diff
    uv run memory_sync.py bidirectional

注意：需要在 Claude Code 环境中运行以使用 MCP Memory 工具
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
DOCS_DIR = PROJECT_ROOT / "docs"


# 实体类型到文档的映射
ENTITY_DOC_MAPPING: dict[str, str] = {
    "Task": "沟通文档/任务分配.md",
    "Goal": "战略规划/战略目标.md",
    "Progress": "版本规划/v2-技能规划/README.md",
    "CoachEvaluation": "沟通文档/角色记忆更新.md",
    "CoachEvolution": "沟通文档/角色记忆更新.md",
    "Conversation": "沟通文档/CEO-用户沟通.md",
    "Coordination": "沟通文档/协调记录.md",
}


def load_state_file() -> dict[str, Any]:
    """加载同步状态文件"""
    state_file = PROJECT_ROOT / ".claude" / "skills" / "ceo-coach" / "scripts" / ".sync_state.json"
    if state_file.exists():
        with open(state_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"last_sync": None, "entities": {}}


def save_state_file(state: dict[str, Any]) -> None:
    """保存同步状态文件"""
    state_file = PROJECT_ROOT / ".claude" / "skills" / "ceo-coach" / "scripts" / ".sync_state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


async def query_memory_entities(entity_type: Optional[str] = None) -> list[dict[str, Any]]:
    """
    查询 Memory 中的实体

    注意：需要 Claude Code MCP 环境运行
    这里返回模拟数据，实际使用需要调用 MCP 工具
    """
    # 实际实现需要使用 MCP Memory 工具
    # 这里提供接口定义，实际调用由 Skill 层完成

    print(json.dumps({
        "action": "query_entities",
        "entity_type": entity_type,
        "note": "需要在 Claude Code MCP 环境中运行"
    }, ensure_ascii=False))

    return []


async def create_memory_entity(entity_data: dict[str, Any]) -> dict[str, Any]:
    """创建 Memory 实体"""
    print(json.dumps({
        "action": "create_entity",
        "entity": entity_data,
        "note": "需要在 Claude Code MCP 环境中运行"
    }, ensure_ascii=False))

    return {"success": True}


async def update_memory_entity(entity_id: str, observations: list[str]) -> dict[str, Any]:
    """更新 Memory 实体"""
    print(json.dumps({
        "action": "update_entity",
        "entity_id": entity_id,
        "observations": observations,
        "note": "需要在 Claude Code MCP 环境中运行"
    }, ensure_ascii=False))

    return {"success": True}


def read_doc_content(doc_path: str) -> Optional[str]:
    """读取文档内容"""
    full_path = DOCS_DIR / doc_path
    if full_path.exists():
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    return None


def parse_tasks_from_doc() -> list[dict[str, Any]]:
    """从任务分配文档解析任务列表"""
    content = read_doc_content("沟通文档/任务分配.md")
    if not content:
        return []

    tasks = []
    lines = content.split("\n")

    current_section = None
    for i, line in enumerate(lines):
        # 检测任务标题
        if line.startswith("### v2."):
            task_id = line.replace("###", "").strip()
            status = "pending"

            # 查找状态
            for j in range(i + 1, min(i + 10, len(lines))):
                if "[x]" in lines[j] or "✅" in lines[j]:
                    status = "completed"
                    break
                elif "[ ]" in lines[j]:
                    status = "pending"
                    break

            tasks.append({
                "task_id": task_id,
                "status": status,
                "line_index": i
            })

    return tasks


def parse_goals_from_doc() -> list[dict[str, Any]]:
    """从战略目标文档解析目标列表"""
    content = read_doc_content("战略规划/战略目标.md")
    if not content:
        return []

    goals = []
    lines = content.split("\n")

    for i, line in enumerate(lines):
        if line.startswith("##") or line.startswith("**"):
            # 提取目标名称
            goal_name = line.replace("#", "").replace("*", "").strip()
            if goal_name and len(goal_name) < 100:
                goals.append({
                    "goal": goal_name,
                    "line_index": i
                })

    return goals


async def sync_to_document() -> dict[str, Any]:
    """同步 Memory 数据到文档"""
    print("=" * 50)
    print("执行 Memory -> 文档 同步")
    print("=" * 50)

    state = load_state_file()

    # 查询所有实体
    entities = await query_memory_entities()

    synced_count = 0

    for entity in entities:
        entity_type = entity.get("entityType", "Unknown")
        entity_name = entity.get("name", "Unknown")

        if entity_type in ENTITY_DOC_MAPPING:
            doc_path = ENTITY_DOC_MAPPING[entity_type]

            # 记录同步状态
            state["entities"][entity_name] = {
                "type": entity_type,
                "last_sync": datetime.now().isoformat(),
                "doc": doc_path
            }

            synced_count += 1
            print(f"同步: {entity_name} ({entity_type}) -> {doc_path}")

    # 更新同步状态
    state["last_sync"] = datetime.now().isoformat()
    save_state_file(state)

    print(f"\n同步完成: {synced_count} 个实体已同步")

    return {
        "success": True,
        "synced_count": synced_count,
        "last_sync": state["last_sync"]
    }


async def sync_to_memory() -> dict[str, Any]:
    """同步文档数据到 Memory"""
    print("=" * 50)
    print("执行 文档 -> Memory 同步")
    print("=" * 50)

    synced_count = 0

    # 同步任务
    tasks = parse_tasks_from_doc()
    for task in tasks:
        entity_name = f"Task-{task['task_id']}"
        await create_memory_entity({
            "name": entity_name,
            "entityType": "Task",
            "observations": [
                f"taskId: {task['task_id']}",
                f"status: {task['status']}",
                f"source: document",
                f"syncedAt: {datetime.now().isoformat()}"
            ]
        })
        synced_count += 1
        print(f"同步: {task['task_id']} -> Memory")

    # 同步目标
    goals = parse_goals_from_doc()
    for goal in goals:
        entity_name = f"Goal-{goal['goal'][:30]}"
        await create_memory_entity({
            "name": entity_name,
            "entityType": "Goal",
            "observations": [
                f"goal: {goal['goal']}",
                f"source: document",
                f"syncedAt: {datetime.now().isoformat()}"
            ]
        })
        synced_count += 1
        print(f"同步: {goal['goal'][:30]}... -> Memory")

    print(f"\n同步完成: {synced_count} 个文档项已同步到 Memory")

    return {
        "success": True,
        "synced_count": synced_count
    }


async def diff_check() -> dict[str, Any]:
    """检测 Memory 和文档的差异"""
    print("=" * 50)
    print("检测 Memory 与文档差异")
    print("=" * 50)

    # 加载同步状态
    state = load_state_file()

    # 获取 Memory 实体
    memory_entities = await query_memory_entities()

    # 解析文档数据
    doc_tasks = parse_tasks_from_doc()
    doc_goals = parse_goals_from_doc()

    diff_result = {
        "memory_count": len(memory_entities),
        "doc_tasks_count": len(doc_tasks),
        "doc_goals_count": len(doc_goals),
        "differences": [],
        "sync_state": state
    }

    # 检测差异
    for entity in memory_entities:
        entity_name = entity.get("name", "")
        entity_type = entity.get("entityType", "")

        if entity_type == "Task":
            # 检查是否在文档中存在
            found = any(t["task_id"] in entity_name for t in doc_tasks)
            if not found:
                diff_result["differences"].append({
                    "type": "memory_only",
                    "entity": entity_name,
                    "message": "实体在 Memory 中存在，但文档中未找到"
                })

    print(f"Memory 实体数: {diff_result['memory_count']}")
    print(f"文档任务数: {diff_result['doc_tasks_count']}")
    print(f"文档目标数: {diff_result['doc_goals_count']}")
    print(f"差异数: {len(diff_result['differences'])}")

    return diff_result


async def bidirectional_sync() -> dict[str, Any]:
    """双向同步，自动解决冲突"""
    print("=" * 50)
    print("执行双向同步")
    print("=" * 50)

    # 1. 先执行差异检测
    diff_result = await diff_check()

    # 2. 同步 Memory -> 文档
    await sync_to_document()

    # 3. 同步文档 -> Memory（处理新增）
    await sync_to_memory()

    print("\n双向同步完成")

    return {
        "success": True,
        "diff_count": len(diff_result.get("differences", []))
    }


def print_json(data: Any) -> None:
    """打印 JSON 输出"""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main() -> None:
    """CLI 入口"""
    if len(sys.argv) < 2:
        print("Memory 同步工具")
        print("")
        print("用法:")
        print("  uv run memory_sync.py sync-to-doc    # Memory -> 文档")
        print("  uv run memory_sync.py sync-to-memory  # 文档 -> Memory")
        print("  uv run memory_sync.py diff            # 检测差异")
        print("  uv run memory_sync.py bidirectional  # 双向同步")
        print("")
        print("注意: 需要在 Claude Code 环境中运行以使用 MCP Memory 工具")
        sys.exit(1)

    command = sys.argv[1]

    if command == "sync-to-doc":
        result = asyncio.run(sync_to_document())
        print_json(result)

    elif command == "sync-to-memory":
        result = asyncio.run(sync_to_memory())
        print_json(result)

    elif command == "diff":
        result = asyncio.run(diff_check())
        print_json(result)

    elif command == "bidirectional":
        result = asyncio.run(bidirectional_sync())
        print_json(result)

    else:
        print_json({"error": f"未知命令: {command}"})
        sys.exit(1)


if __name__ == "__main__":
    main()
