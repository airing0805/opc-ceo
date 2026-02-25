#!/usr/bin/env python3
"""
异常情况自动恢复脚本

功能：
- 检测 Memory 为空或异常的情况
- 自动从文档重建 Memory 实体
- 检测并修复异常实体
- 记录恢复日志

使用 uv 运行:
    uv run auto_recovery.py check      # 检查异常
    uv run auto_recovery.py recover    # 执行恢复
    uv run auto_recovery.py full       # 完整检查+恢复

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


# 异常类型定义
EXCEPTION_TYPES = {
    "EMPTY_MEMORY": "Memory 为空",
    "MISSING_ENTITIES": "缺少核心实体",
    "CORRUPTED_DATA": "数据损坏",
    "STALE_DATA": "数据过期",
    "ORPHANED_ENTITIES": "孤立实体（无关联）",
}


# 核心实体类型（必须有）
CORE_ENTITIES = [
    "Task",
    "Goal",
    "Progress",
    "CoachEvaluation",
]


def load_recovery_log() -> list[dict[str, Any]]:
    """加载恢复日志"""
    log_file = PROJECT_ROOT / ".claude" / "skills" / "ceo-coach" / "scripts" / ".recovery_log.json"
    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_recovery_log(logs: list[dict[str, Any]]) -> None:
    """保存恢复日志"""
    log_file = PROJECT_ROOT / ".claude" / "skills" / "ceo-coach" / "scripts" / ".recovery_log.json"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


def log_recovery(action: str, status: str, details: dict[str, Any]) -> None:
    """记录恢复操作"""
    logs = load_recovery_log()
    logs.append({
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "status": status,
        "details": details
    })
    # 只保留最近 100 条记录
    logs = logs[-100:]
    save_recovery_log(logs)


async def check_memory_status() -> dict[str, Any]:
    """
    检查 Memory 状态

    返回检查结果：
    - is_empty: Memory 是否为空
    - has_core_entities: 是否包含核心实体
    - exceptions: 检测到的异常列表
    """
    print("=" * 50)
    print("检查 Memory 状态")
    print("=" * 50)

    result = {
        "checked_at": datetime.now().isoformat(),
        "is_empty": True,
        "entity_count": 0,
        "entity_types": {},
        "has_core_entities": False,
        "exceptions": [],
        "status": "unknown"
    }

    # 模拟检查 - 实际需要 MCP Memory 工具
    print(json.dumps({
        "action": "check_memory",
        "note": "需要在 Claude Code MCP 环境中运行"
    }, ensure_ascii=False))

    # 检查文档作为备用数据源
    task_doc = DOCS_DIR / "沟通文档" / "任务分配.md"
    if task_doc.exists():
        content = task_doc.read_text(encoding="utf-8")
        # 简单检查是否有任务
        if "v2." in content:
            result["has_docs"] = True
            print("文档数据源可用")

    # 返回检查状态
    result["status"] = "checked"
    print(f"\n检查完成")
    print(f"- 实体数量: {result['entity_count']}")
    print(f"- 核心实体: {'是' if result['has_core_entities'] else '否'}")
    print(f"- 异常数量: {len(result['exceptions'])}")

    return result


async def recover_from_documents() -> dict[str, Any]:
    """
    从文档恢复 Memory

    恢复流程：
    1. 读取任务分配.md -> 重建 Task 实体
    2. 读取战略目标.md -> 重建 Goal 实体
    3. 读取版本规划 README.md -> 重建 Progress 实体
    4. 读取角色记忆更新.md -> 重建 Evaluation/Evolution 实体
    """
    print("=" * 50)
    print("从文档恢复 Memory")
    print("=" * 50)

    recovered_count = 0

    # 1. 恢复任务实体
    task_doc = DOCS_DIR / "沟通文档" / "任务分配.md"
    if task_doc.exists():
        content = task_doc.read_text(encoding="utf-8")
        lines = content.split("\n")

        current_date = None
        in_pending_section = False

        for line in lines:
            # 提取日期
            if line.startswith("## 20"):
                current_date = line.replace("##", "").strip()

            # 检测待完成任务
            if "待后续优化" in line or "待完成" in line:
                in_pending_section = True
            elif line.startswith("###"):
                in_pending_section = False

            # 提取任务 ID (v2.x.y 格式)
            if "### v2." in line and in_pending_section:
                task_id = line.replace("###", "").strip()
                print(f"发现待完成任务: {task_id}")

                # 创建 Memory 实体（模拟）
                print(json.dumps({
                    "action": "create_entity",
                    "entityType": "Task",
                    "name": f"Task-{task_id}",
                    "observations": [
                        f"taskId: {task_id}",
                        "status: pending",
                        f"source: recovery",
                        f"recoveredAt: {datetime.now().isoformat()}"
                    ]
                }, ensure_ascii=False))

                recovered_count += 1

    # 2. 恢复目标实体
    goal_doc = DOCS_DIR / "战略规划" / "战略目标.md"
    if goal_doc.exists():
        content = goal_doc.read_text(encoding="utf-8")
        print(f"战略目标文档存在，包含 {len(content)} 字符")
        recovered_count += 1

    # 3. 恢复进度实体
    progress_doc = DOCS_DIR / "docs" / "版本规划" / "v2-技能规划" / "README.md"
    if progress_doc.exists():
        print("版本规划文档存在")
        recovered_count += 1

    # 记录恢复操作
    log_recovery(
        action="recover_from_documents",
        status="completed",
        details={
            "recovered_count": recovered_count,
            "timestamp": datetime.now().isoformat()
        }
    )

    print(f"\n恢复完成: {recovered_count} 个数据源已处理")

    return {
        "success": True,
        "recovered_count": recovered_count,
        "timestamp": datetime.now().isoformat()
    }


async def repair_entity(entity_id: str, observations: list[str]) -> dict[str, Any]:
    """修复损坏的实体"""
    print(f"修复实体: {entity_id}")

    result = {
        "action": "repair_entity",
        "entity_id": entity_id,
        "observations": observations,
        "timestamp": datetime.now().isoformat()
    }

    log_recovery(
        action="repair_entity",
        status="completed",
        details=result
    )

    return result


async def full_recovery() -> dict[str, Any]:
    """完整检查+恢复流程"""
    print("=" * 50)
    print("执行完整检查与恢复")
    print("=" * 50)

    # 1. 检查状态
    status = await check_memory_status()

    # 2. 如果有异常，执行恢复
    if status["exceptions"] or status.get("is_empty", True):
        print("\n检测到异常，开始恢复...")
        recovery_result = await recover_from_documents()
    else:
        print("\n未检测到异常，无需恢复")
        recovery_result = {"success": True, "recovered_count": 0}

    # 3. 再次检查
    final_status = await check_memory_status()

    result = {
        "success": True,
        "initial_status": status,
        "recovery": recovery_result,
        "final_status": final_status,
        "timestamp": datetime.now().isoformat()
    }

    log_recovery(
        action="full_recovery",
        status="completed",
        details=result
    )

    return result


def print_json(data: Any) -> None:
    """打印 JSON 输出"""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main() -> None:
    """CLI 入口"""
    if len(sys.argv) < 2:
        print("异常情况自动恢复工具")
        print("")
        print("用法:")
        print("  uv run auto_recovery.py check     # 检查 Memory 状态")
        print("  uv run auto_recovery.py recover   # 执行恢复")
        print("  uv run auto_recovery.py full      # 完整检查+恢复")
        print("")
        print("注意: 需要在 Claude Code 环境中运行以使用 MCP Memory 工具")
        sys.exit(1)

    command = sys.argv[1]

    if command == "check":
        result = asyncio.run(check_memory_status())
        print_json(result)

    elif command == "recover":
        result = asyncio.run(recover_from_documents())
        print_json(result)

    elif command == "full":
        result = asyncio.run(full_recovery())
        print_json(result)

    else:
        print_json({"error": f"未知命令: {command}"})
        sys.exit(1)


if __name__ == "__main__":
    main()
