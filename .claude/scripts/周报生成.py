#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
周报自动生成脚本

功能:
1. 从任务分配.md 提取本周完成任务
2. 从工作日志提取每日工作记录
3. 生成本周总结和下周计划

使用方法:
    python 周报生成.py [--week WXX] [--year YYYY]

示例:
    python 周报生成.py --week W09 --year 2026
    python 周报生成.py  # 默认当前周
"""

import os
import re
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class WeeklyReportGenerator:
    """周报生成器"""

    def __init__(self, base_dir: str = None):
        """初始化

        Args:
            base_dir: 项目根目录，默认自动检测
        """
        if base_dir is None:
            # 自动检测项目根目录
            self.base_dir = Path(__file__).parent.parent.parent
        else:
            self.base_dir = Path(base_dir)

        self.task_file = self.base_dir / "docs" / "沟通文档" / "任务分配.md"
        self.daily_log_dir = self.base_dir / "docs" / "运营规划" / "工作日志" / "日报"
        self.weekly_log_dir = self.base_dir / "docs" / "运营规划" / "工作日志" / "周报"
        self.config_file = self.base_dir / ".claude" / "config.json"

        # 加载配置
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """加载配置文件"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def get_week_range(self, year: int, week: int) -> Tuple[datetime, datetime]:
        """获取指定周的日期范围

        Args:
            year: 年份
            week: 周数 (1-53)

        Returns:
            (周一日期, 周日日期)
        """
        # ISO 周从周一开始
        first_day = datetime.strptime(f"{year}-W{week:02d}-1", "%Y-W%W-%w")
        last_day = first_day + timedelta(days=6)
        return first_day, last_day

    def get_current_week(self) -> Tuple[int, int]:
        """获取当前年份和周数"""
        now = datetime.now()
        iso_calendar = now.isocalendar()
        return iso_calendar[0], iso_calendar[1]

    def parse_task_file(self) -> Dict[str, List[Dict]]:
        """解析任务分配文件

        Returns:
            按日期分组的任务字典 {date_str: [task_dict, ...]}
        """
        if not self.task_file.exists():
            return {}

        with open(self.task_file, 'r', encoding='utf-8') as f:
            content = f.read()

        tasks_by_date = {}
        current_date = None
        current_version = None

        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # 检测日期标题 ## 2026-02-25
            date_match = re.match(r'^## (\d{4}-\d{2}-\d{2})$', line)
            if date_match:
                current_date = date_match.group(1)
                if current_date not in tasks_by_date:
                    tasks_by_date[current_date] = []
                i += 1
                continue

            # 检测版本号 ### v2.3.1 - Coach 自我进化优化
            version_match = re.match(r'^### (v[\d.]+) - (.+)$', line)
            if version_match and current_date:
                current_version = version_match.group(1)
                i += 1
                continue

            # 检测任务表格行 | TASK-2026-02-26-001 | ... |
            task_match = re.match(r'^\| (TASK-[\d-]+) \| (.+?) \| (.+?) \|', line)
            if task_match and current_date:
                task_id = task_match.group(1)
                title = task_match.group(2).strip()
                status_str = task_match.group(3).strip()

                # 解析状态
                status = self._parse_status(status_str)

                task = {
                    'id': task_id,
                    'title': title,
                    'status': status,
                    'version': current_version,
                    'date': current_date
                }
                tasks_by_date[current_date].append(task)

            i += 1

        return tasks_by_date

    def _parse_status(self, status_str: str) -> str:
        """解析任务状态字符串

        Args:
            status_str: 状态字符串如 '[x]', '✅ 完成', '⚠️ 阻塞' 等

        Returns:
            标准化状态: 'completed', 'pending', 'blocked', 'in_progress'
        """
        status_str = status_str.lower()

        if '✅' in status_str or '[x]' in status_str or '完成' in status_str:
            return 'completed'
        elif '⚠️' in status_str or '阻塞' in status_str:
            return 'blocked'
        elif '🚧' in status_str or '进行' in status_str:
            return 'in_progress'
        else:
            return 'pending'

    def filter_tasks_by_week(self, tasks_by_date: Dict[str, List[Dict]],
                             start_date: datetime, end_date: datetime) -> List[Dict]:
        """筛选指定周的任务

        Args:
            tasks_by_date: 按日期分组的任务
            start_date: 周一
            end_date: 周日

        Returns:
            本周任务列表
        """
        week_tasks = []
        current = start_date

        while current <= end_date:
            date_str = current.strftime('%Y-%m-%d')
            if date_str in tasks_by_date:
                week_tasks.extend(tasks_by_date[date_str])
            current += timedelta(days=1)

        return week_tasks

    def calculate_statistics(self, tasks: List[Dict]) -> Dict:
        """计算任务统计

        Args:
            tasks: 任务列表

        Returns:
            统计字典
        """
        stats = {
            'total': len(tasks),
            'completed': 0,
            'pending': 0,
            'blocked': 0,
            'in_progress': 0,
            'by_priority': {'P0': 0, 'P1': 0, 'P2': 0, 'P3': 0},
            'by_type': {}
        }

        for task in tasks:
            status = task.get('status', 'pending')
            stats[status] = stats.get(status, 0) + 1

            # 按类型统计（基于标题关键词）
            title = task.get('title', '')
            task_type = self._classify_task_type(title)
            stats['by_type'][task_type] = stats['by_type'].get(task_type, 0) + 1

        return stats

    def _classify_task_type(self, title: str) -> str:
        """根据标题分类任务类型"""
        title_lower = title.lower()

        if '文档' in title or 'doc' in title_lower:
            return '文档编写'
        elif '架构' in title or '设计' in title:
            return '架构设计'
        elif 'bug' in title_lower or '修复' in title:
            return 'Bug 修复'
        elif '测试' in title:
            return '测试'
        elif '优化' in title or '改进' in title:
            return '优化改进'
        else:
            return '功能开发'

    def generate_report(self, year: int = None, week: int = None) -> str:
        """生成周报

        Args:
            year: 年份，默认当前年
            week: 周数，默认当前周

        Returns:
            周报 Markdown 内容
        """
        if year is None or week is None:
            year, week = self.get_current_week()

        start_date, end_date = self.get_week_range(year, week)
        date_range = f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}"

        # 解析任务
        tasks_by_date = self.parse_task_file()
        week_tasks = self.filter_tasks_by_week(tasks_by_date, start_date, end_date)
        stats = self.calculate_statistics(week_tasks)

        # 生成报告
        report_lines = []

        # 标题
        report_lines.append(f"# 周报 - {year}-W{week:02d}")
        report_lines.append("")
        report_lines.append(f"> 第 {week} 周工作总结（{date_range}）")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")

        # 本周概览
        report_lines.append("## 本周概览")
        report_lines.append("")
        report_lines.append("| 指标 | 本周值 | 上周值 | 变化 |")
        report_lines.append("|------|--------|--------|------|")
        completion_rate = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
        report_lines.append(f"| 完成任务数 | {stats['completed']} | - | - |")
        report_lines.append(f"| 任务总数 | {stats['total']} | - | - |")
        report_lines.append(f"| 任务完成率 | {completion_rate:.1f}% | - | - |")
        report_lines.append("")

        # 任务完成统计
        report_lines.append("## 任务完成统计")
        report_lines.append("")
        report_lines.append("### 按状态")
        report_lines.append("")
        report_lines.append("| 状态 | 数量 |")
        report_lines.append("|------|------|")
        report_lines.append(f"| 已完成 | {stats['completed']} |")
        report_lines.append(f"| 进行中 | {stats['in_progress']} |")
        report_lines.append(f"| 待执行 | {stats['pending']} |")
        report_lines.append(f"| 阻塞 | {stats['blocked']} |")
        report_lines.append("")

        # 按类型统计
        if stats['by_type']:
            report_lines.append("### 按类型")
            report_lines.append("")
            report_lines.append("| 类型 | 数量 |")
            report_lines.append("|------|------|")
            for task_type, count in sorted(stats['by_type'].items(), key=lambda x: -x[1]):
                report_lines.append(f"| {task_type} | {count} |")
            report_lines.append("")

        # 本周完成任务清单
        completed_tasks = [t for t in week_tasks if t['status'] == 'completed']
        if completed_tasks:
            report_lines.append("## 本周完成任务")
            report_lines.append("")
            report_lines.append("| 任务 ID | 标题 | 版本 | 日期 |")
            report_lines.append("|---------|------|------|------|")
            for task in completed_tasks:
                report_lines.append(f"| {task['id']} | {task['title']} | {task.get('version', '-')} | {task['date']} |")
            report_lines.append("")

        # 未完成任务
        pending_tasks = [t for t in week_tasks if t['status'] != 'completed']
        if pending_tasks:
            report_lines.append("## 未完成任务")
            report_lines.append("")
            report_lines.append("| 任务 ID | 标题 | 状态 | 原因 |")
            report_lines.append("|---------|------|------|------|")
            for task in pending_tasks:
                status_cn = {
                    'pending': '待执行',
                    'blocked': '阻塞',
                    'in_progress': '进行中'
                }.get(task['status'], task['status'])
                report_lines.append(f"| {task['id']} | {task['title']} | {status_cn} | - |")
            report_lines.append("")

        # 下周计划
        report_lines.append("## 下周计划")
        report_lines.append("")
        report_lines.append("### 重点目标")
        report_lines.append("")
        report_lines.append("1. [根据任务分配.md中的待执行任务填写]")
        report_lines.append("2. [根据战略目标对齐填写]")
        report_lines.append("3. [根据本周遗留问题填写]")
        report_lines.append("")
        report_lines.append("### 待执行任务")
        report_lines.append("")
        report_lines.append("| 优先级 | 任务 ID | 标题 | 预计时间 |")
        report_lines.append("|--------|---------|------|----------|")
        report_lines.append("| P0 | TASK-YYYY-MM-DD-NNN | 任务描述 | Nh |")
        report_lines.append("")

        # 每日回顾（简化版）
        report_lines.append("## 每日工作回顾")
        report_lines.append("")
        report_lines.append("| 日期 | 完成任务 | 重要事件 |")
        report_lines.append("|------|----------|----------|")

        current = start_date
        weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        day_idx = 0

        while current <= end_date:
            date_str = current.strftime('%Y-%m-%d')
            day_tasks = [t for t in week_tasks if t.get('date') == date_str]
            completed_count = len([t for t in day_tasks if t['status'] == 'completed'])
            weekday = weekday_names[day_idx]
            report_lines.append(f"| {weekday} ({date_str[-5:]}) | {completed_count} 个 | - |")
            current += timedelta(days=1)
            day_idx += 1

        report_lines.append("")

        # 经验总结
        report_lines.append("## 经验总结")
        report_lines.append("")
        report_lines.append("### 成功经验")
        report_lines.append("")
        report_lines.append("1. [根据本周工作填写]")
        report_lines.append("")
        report_lines.append("### 待改进")
        report_lines.append("")
        report_lines.append("1. [根据本周问题填写]")
        report_lines.append("")

        # 更新历史
        report_lines.append("---")
        report_lines.append("")
        report_lines.append("## 更新历史")
        report_lines.append("")
        report_lines.append("| 时间 | 变更内容 |")
        report_lines.append("|------|----------|")
        report_lines.append(f"| {datetime.now().strftime('%Y-%m-%d %H:%M')} | 自动生成周报 |")

        return '\n'.join(report_lines)

    def save_report(self, year: int = None, week: int = None, output_file: str = None) -> str:
        """保存周报到文件

        Args:
            year: 年份
            week: 周数
            output_file: 输出文件路径，默认保存到周报目录

        Returns:
            保存的文件路径
        """
        report = self.generate_report(year, week)

        if year is None or week is None:
            year, week = self.get_current_week()

        if output_file is None:
            # 确保目录存在
            self.weekly_log_dir.mkdir(parents=True, exist_ok=True)
            output_file = self.weekly_log_dir / f"{year}-W{week:02d}.md"
        else:
            output_file = Path(output_file)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)

        return str(output_file)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='周报自动生成脚本')
    parser.add_argument('--week', '-w', type=int, help='周数 (如 9 表示 W09)')
    parser.add_argument('--year', '-y', type=int, help='年份 (如 2026)')
    parser.add_argument('--output', '-o', type=str, help='输出文件路径')
    parser.add_argument('--print', '-p', action='store_true', help='打印到控制台')

    args = parser.parse_args()

    generator = WeeklyReportGenerator()

    year = args.year
    week = args.week

    if args.print:
        # 打印到控制台
        report = generator.generate_report(year, week)
        print(report)
    else:
        # 保存到文件
        output_path = generator.save_report(year, week, args.output)
        print(f"周报已生成: {output_path}")


if __name__ == '__main__':
    main()
