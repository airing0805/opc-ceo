# -*- coding: utf-8 -*-
"""
发布追踪器模块

用于记录和追踪内容发布数据，集成 MCP Memory 进行知识图谱存储。

功能：
1. 发布后自动采集装饰器
2. 查询已发布内容（按平台、时间、选题ID）
3. 统计功能（各平台发布数量、每日发布趋势）
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Optional, List, Dict, Any
import json


class PostStatus(Enum):
    """发布状态枚举"""
    DRAFT = "draft"
    PUBLISHED = "published"
    FAILED = "failed"


# 存储在内存中的发布记录（用于查询和统计）
# 在实际生产环境中，可替换为数据库或持久化存储
_publish_records: Dict[str, PublishRecord] = {}


# ============================================================
# 1. 发布后自动采集装饰器
# ============================================================

class PublishResult:
    """发布结果封装类，用于装饰器获取发布结果"""

    def __init__(
        self,
        success: bool,
        title: str = "",
        topic_id: str = "",
        platform: str = "",
        account: str = "",
        post_url: Optional[str] = None,
        ai_score: float = 0.0,
        word_count: int = 0,
        case_count: int = 0,
        error_message: Optional[str] = None
    ):
        self.success = success
        self.title = title
        self.topic_id = topic_id
        self.platform = platform
        self.account = account
        self.post_url = post_url
        self.ai_score = ai_score
        self.word_count = word_count
        self.case_count = case_count
        self.error_message = error_message


def auto_track_publish(platform_name: str):
    """Auto-track publish decorator.

    Args:
        platform_name: Platform name, e.g., "zhihu", "jianshu"

    Usage:
        @auto_track_publish("zhihu")
        def publish_to_zhihu(content: dict) -> PublishResult:
            # publish logic
            return PublishResult(success=True, title="...", topic_id="...")
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 执行发布函数
            result = func(*args, **kwargs)

            # 支持两种返回类型：PublishResult 或普通返回值
            if isinstance(result, PublishResult):
                publish_result = result
            else:
                # 假设返回的是包含成功标志的结果对象
                publish_result = result

            # 仅在成功时采集记录
            if hasattr(publish_result, 'success') and publish_result.success:
                try:
                    # 创建发布记录
                    record = create_publish_record(
                        title=publish_result.title,
                        topic_id=publish_result.topic_id,
                        platform=platform_name,
                        account=publish_result.account,
                        ai_score=publish_result.ai_score,
                        word_count=publish_result.word_count,
                        case_count=publish_result.case_count,
                        post_url=publish_result.post_url,
                        status=PostStatus.PUBLISHED,
                        error_message=None
                    )

                    # 保存到内存和 MCP Memory
                    _publish_records[record.record_id] = record
                    save_to_memory(record)

                    print(f"[自动采集] 已记录发布: {record.title} -> {platform_name}")
                except Exception as e:
                    print(f"[自动采集] 记录失败: {e}")
            elif hasattr(publish_result, 'success') and not publish_result.success:
                # 发布失败也记录
                error_msg = getattr(publish_result, 'error_message', '未知错误')
                try:
                    record = create_publish_record(
                        title=getattr(publish_result, 'title', '未知'),
                        topic_id=getattr(publish_result, 'topic_id', '未知'),
                        platform=platform_name,
                        account=getattr(publish_result, 'account', ''),
                        ai_score=getattr(publish_result, 'ai_score', 0.0),
                        word_count=getattr(publish_result, 'word_count', 0),
                        case_count=getattr(publish_result, 'case_count', 0),
                        status=PostStatus.FAILED,
                        error_message=error_msg
                    )
                    _publish_records[record.record_id] = record
                except Exception as e:
                    print(f"[自动采集] 记录失败状态失败: {e}")

            return result
        return wrapper
    return decorator


# ============================================================
# 2. 查询功能
# ============================================================

def query_by_platform(platform: str) -> List[PublishRecord]:
    """Query published content by platform.

    Args:
        platform: Platform name

    Returns:
        List of publish records for the platform
    """
    return [
        record for record in _publish_records.values()
        if record.platform == platform and record.status == PostStatus.PUBLISHED
    ]


def query_by_topic_id(topic_id: str) -> List[PublishRecord]:
    """Query published content by topic ID.

    Args:
        topic_id: Topic ID

    Returns:
        List of publish records for the topic
    """
    return [
        record for record in _publish_records.values()
        if record.topic_id == topic_id
    ]


def query_by_date_range(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[PublishRecord]:
    """Query published content by date range.

    Args:
        start_date: Start date (exclusive), defaults to today start
        end_date: End date (exclusive), defaults to now

    Returns:
        List of publish records in the date range
    """
    if start_date is None:
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if end_date is None:
        end_date = datetime.now()

    return [
        record for record in _publish_records.values()
        if start_date <= record.publish_time < end_date
        and record.status == PostStatus.PUBLISHED
    ]


def query_by_date(date: datetime) -> List[PublishRecord]:
    """Query publish records for a specific date.

    Args:
        date: Query date

    Returns:
        List of publish records for the date
    """
    start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    return query_by_date_range(start_of_day, end_of_day)


def query_all_published() -> List[PublishRecord]:
    """Query all published content.

    Returns:
        List of all published records
    """
    return [
        record for record in _publish_records.values()
        if record.status == PostStatus.PUBLISHED
    ]


def query_failed() -> List[PublishRecord]:
    """Query all failed publish records.

    Returns:
        List of all failed records
    """
    return [
        record for record in _publish_records.values()
        if record.status == PostStatus.FAILED
    ]


# ============================================================
# 3. 统计功能
# ============================================================

def count_by_platform() -> Dict[str, int]:
    """Count publish count by platform.

    Returns:
        Dict mapping platform name to publish count
    """
    counts: Dict[str, int] = {}
    for record in _publish_records.values():
        if record.status == PostStatus.PUBLISHED:
            counts[record.platform] = counts.get(record.platform, 0) + 1
    return counts


def count_by_platform_detailed() -> Dict[str, Dict[str, Any]]:
    """Get detailed stats by platform.

    Returns:
        Dict mapping platform name to detailed stats
    """
    stats: Dict[str, Dict[str, Any]] = {}

    for record in _publish_records.values():
        if record.status == PostStatus.PUBLISHED:
            platform = record.platform
            if platform not in stats:
                stats[platform] = {
                    "count": 0,
                    "total_words": 0,
                    "total_cases": 0,
                    "avg_ai_score": 0.0,
                    "records": []
                }

            stats[platform]["count"] += 1
            stats[platform]["total_words"] += record.word_count
            stats[platform]["total_cases"] += record.case_count
            stats[platform]["records"].append(record.record_id)

    # 计算平均AI评分
    for platform, data in stats.items():
        if data["count"] > 0:
            records = [
                r for r in _publish_records.values()
                if r.platform == platform and r.status == PostStatus.PUBLISHED
            ]
            avg_score = sum(r.ai_score for r in records) / len(records)
            data["avg_ai_score"] = round(avg_score, 2)

    return stats


def daily_trend(days: int = 7) -> Dict[str, int]:
    """Get daily publish trend.

    Args:
        days: Number of days to include, defaults to 7

    Returns:
        Dict mapping date string to publish count
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    trend: Dict[str, int] = {}

    # 初始化所有日期
    current = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    while current <= end_date:
        date_key = current.strftime('%Y-%m-%d')
        trend[date_key] = 0
        current += timedelta(days=1)

    # 统计每日数量
    for record in _publish_records.values():
        if record.status == PostStatus.PUBLISHED:
            date_key = record.publish_time.strftime('%Y-%m-%d')
            if date_key in trend:
                trend[date_key] += 1

    return trend


def daily_trend_detailed(days: int = 7) -> List[Dict[str, Any]]:
    """Get detailed daily publish trend.

    Args:
        days: Number of days to include, defaults to 7

    Returns:
        List of daily detailed stats
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    result = []

    # 遍历每一天
    current = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    while current <= end_date:
        next_day = current + timedelta(days=1)

        # 筛选当天的记录
        day_records = [
            r for r in _publish_records.values()
            if current <= r.publish_time < next_day
            and r.status == PostStatus.PUBLISHED
        ]

        # 按平台统计
        platform_counts: Dict[str, int] = {}
        for record in day_records:
            platform_counts[record.platform] = platform_counts.get(record.platform, 0) + 1

        result.append({
            "date": current.strftime('%Y-%m-%d'),
            "total": len(day_records),
            "by_platform": platform_counts,
            "records": [r.record_id for r in day_records]
        })

        current = next_day

    return result


def get_statistics_summary() -> Dict[str, Any]:
    """Get statistics summary.

    Returns:
        Dict containing statistics summary
    """
    published = query_all_published()
    failed = query_failed()

    total_words = sum(r.word_count for r in published)
    total_cases = sum(r.case_count for r in published)
    avg_ai_score = sum(r.ai_score for r in published) / len(published) if published else 0

    return {
        "total_published": len(published),
        "total_failed": len(failed),
        "total_words": total_words,
        "total_cases": total_cases,
        "avg_ai_score": round(avg_ai_score, 2),
        "by_platform": count_by_platform(),
        "daily_trend": daily_trend(7)
    }


# ============================================================
# 数据模型和基础函数
# ============================================================


@dataclass
class PublishRecord:
    """发布记录数据模型"""
    # 内容信息
    title: str
    topic_id: str  # 选题ID
    publish_time: datetime
    
    # 平台信息
    platform: str
    account: str
    post_url: Optional[str]
    
    # 质量信息
    ai_score: float  # AI味评分
    word_count: int
    case_count: int
    
    # 追踪信息
    record_id: str  # 记录ID，格式：PUB-YYYY-MM-DD-NNN
    status: PostStatus
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        data = asdict(self)
        data['status'] = self.status.value
        data['publish_time'] = self.publish_time.isoformat()
        return data
    
    def to_entity(self) -> dict:
        """转换为 MCP Memory 实体格式"""
        return {
            "entityType": "PublishRecord",
            "name": self.record_id,
            "observations": [
                f"标题: {self.title}",
                f"选题ID: {self.topic_id}",
                f"发布时间: {self.publish_time.strftime('%Y-%m-%d %H:%M:%S')}",
                f"平台: {self.platform}",
                f"账号: {self.account}",
                f"文章链接: {self.post_url or '未生成'}",
                f"AI味评分: {self.ai_score}",
                f"字数: {self.word_count}",
                f"案例数: {self.case_count}",
                f"状态: {self.status.value}",
                f"错误信息: {self.error_message or '无'}",
            ]
        }


# 记录ID计数器
_record_id_counter = 0


def generate_record_id() -> str:
    """Generate record ID.

    Format: PUB-YYYY-MM-DD-NNN

    Returns:
        Record ID string
    """
    global _record_id_counter
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    # 使用自增计数器确保唯一性
    _record_id_counter += 1
    seq = str(_record_id_counter).zfill(3)
    return f"PUB-{date_str}-{seq}"


def save_to_memory(record: PublishRecord) -> dict:
    """Save publish record to MCP Memory.

    Args:
        record: PublishRecord object

    Returns:
        MCP Memory API response
    """
    from mcp__memory__create_entities import mcp__memory__create_entities
    
    entity = record.to_entity()
    result = mcp__memory__create_entities(entities=[entity])
    
    # 同时创建关系：内容 -> 已发布到 -> 平台
    _create_publish_relation(record)
    
    return result


def _create_publish_relation(record: PublishRecord) -> None:
    """Create publish relation: topic -> published to -> platform.

    Args:
        record: PublishRecord object
    """
    from mcp__memory__create_relations import mcp__memory__create_relations
    
    relations = [
        {
            "from": record.topic_id,
            "relationType": "已发布到",
            "to": record.platform
        },
        {
            "from": record.record_id,
            "relationType": "关联选题",
            "to": record.topic_id
        }
    ]
    
    try:
        mcp__memory__create_relations(relations=relations)
    except Exception as e:
        # 关系创建失败不影响主流程，只记录日志
        print(f"创建关系失败: {e}")


def batch_save_records(records: List[PublishRecord]) -> List[dict]:
    """Batch save publish records to MCP Memory.

    Args:
        records: List of PublishRecord objects

    Returns:
        List of save results for each record
    """
    results = []
    for record in records:
        result = save_to_memory(record)
        results.append(result)
    return results


def create_publish_record(
    title: str,
    topic_id: str,
    platform: str,
    account: str,
    ai_score: float,
    word_count: int,
    case_count: int,
    post_url: Optional[str] = None,
    status: PostStatus = PostStatus.PUBLISHED,
    error_message: Optional[str] = None
) -> PublishRecord:
    """Create a publish record.

    Args:
        title: Content title
        topic_id: Topic ID
        platform: Platform name
        account: Account name
        ai_score: AI score
        word_count: Word count
        case_count: Case count
        post_url: Article URL
        status: Publish status
        error_message: Error message

    Returns:
        PublishRecord object
    """
    return PublishRecord(
        title=title,
        topic_id=topic_id,
        publish_time=datetime.now(),
        platform=platform,
        account=account,
        post_url=post_url,
        ai_score=ai_score,
        word_count=word_count,
        case_count=case_count,
        record_id=generate_record_id(),
        status=status,
        error_message=error_message
    )


# ============================================================
# 初始化测试数据（仅用于演示）
# ============================================================

def init_demo_data():
    """初始化演示数据"""
    # 添加一些测试记录
    demo_records = [
        {
            "title": "一人公司CEO的时间管理秘诀",
            "topic_id": "TOPIC-2026-02-28-001",
            "platform": "知乎",
            "account": "CEO思考者",
            "ai_score": 0.15,
            "word_count": 3500,
            "case_count": 3,
            "post_url": "https://zhihu.com/p/123456789"
        },
        {
            "title": "如何在低成本下实现高效运营",
            "topic_id": "TOPIC-2026-02-28-002",
            "platform": "简书",
            "account": "CEO思考者",
            "ai_score": 0.12,
            "word_count": 2800,
            "case_count": 2,
            "post_url": "https://jianshu.com/p/987654321"
        },
        {
            "title": "AI辅助内容生产的实战经验",
            "topic_id": "TOPIC-2026-02-28-003",
            "platform": "知乎",
            "account": "CEO思考者",
            "ai_score": 0.18,
            "word_count": 4200,
            "case_count": 4,
            "post_url": "https://zhihu.com/p/111222333"
        },
        {
            "title": "CSDN技术博客写作技巧",
            "topic_id": "TOPIC-2026-02-27-001",
            "platform": "CSDN",
            "account": "技术CEO",
            "ai_score": 0.20,
            "word_count": 5100,
            "case_count": 5,
            "post_url": "https://blog.csdn.net/ceo/article/123"
        },
        {
            "title": "掘金社区的运营心得",
            "topic_id": "TOPIC-2026-02-27-002",
            "platform": "掘金",
            "account": "技术CEO",
            "ai_score": 0.16,
            "word_count": 3800,
            "case_count": 3,
            "post_url": "https://juejin.cn/post/123456789"
        }
    ]

    for data in demo_records:
        record = create_publish_record(**data)
        _publish_records[record.record_id] = record

    return len(demo_records)


def generate_dashboard(days: int = 7) -> str:
    """生成发布数据看板

    Args:
        days: 统计天数，默认7天

    Returns:
        格式化的看板文本
    """
    # 1. 获取统计数据
    platform_stats = count_by_platform_detailed()
    trend = daily_trend_detailed(days)
    summary = get_statistics_summary()

    # 2. 构建平台分布表格
    platform_rows = []
    for platform, stats in sorted(platform_stats.items()):
        platform_rows.append(
            f"| {platform} | {stats['count']} | {stats['total_words']} | {stats['avg_ai_score']} |"
        )
    platform_table = "\n".join(platform_rows) if platform_rows else "| - | - | - | - |"

    # 3. 构建每日趋势表格
    trend_rows = []
    for day in trend:
        platforms_str = ", ".join([f"{p}:{c}" for p, c in day['by_platform'].items()])
        if not platforms_str:
            platforms_str = "-"
        trend_rows.append(
            f"| {day['date']} | {day['total']} | {platforms_str} |"
        )
    trend_table = "\n".join(trend_rows) if trend_rows else "| - | - | - |"

    # 4. 计算总体概览数据
    total = summary['total_published'] + summary['total_failed']
    published = summary['total_published']
    failed = summary['total_failed']
    avg_score = summary['avg_ai_score']

    # 5. 生成看板文本
    dashboard = f"""# 📊 发布数据看板（近{days}天）

## 总体概览
- **总发布数**: {total}
- **成功发布**: {published}
- **发布失败**: {failed}
- **平均AI评分**: {avg_score:.2f}

## 平台分布
| 平台 | 发布数 | 总字数 | 平均AI评分 |
|------|--------|--------|------------|
{platform_table}

## 每日趋势
| 日期 | 发布数 | 平台分布 |
|------|--------|----------|
{trend_table}

---
*数据生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    return dashboard


# ============================================================
# 命令行接口
# ============================================================

def main():
    """命令行入口函数"""
    import argparse
    import sys

    # Windows 环境下配置 UTF-8 输出
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        description="发布追踪器 - 数据统计与看板生成"
    )
    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="生成发布数据看板"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="统计天数，默认7天"
    )
    parser.add_argument(
        "--init-demo",
        action="store_true",
        help="初始化演示数据"
    )

    args = parser.parse_args()

    # 初始化演示数据
    if args.init_demo:
        count = init_demo_data()
        print(f"已初始化 {count} 条演示数据")

    # 生成看板
    if args.dashboard:
        dashboard = generate_dashboard(days=args.days)
        print(dashboard)
        return

    # 默认显示帮助
    parser.print_help()


# 示例用法
if __name__ == "__main__":
    # 优先处理命令行参数
    import sys
    if len(sys.argv) > 1:
        main()
    else:
        # 无参数时运行示例代码
        # 初始化演示数据
        init_demo_data()

        # ====== 1. 自动采集装饰器示例 ======
        print("=" * 50)
        print("1. 自动采集装饰器示例")
        print("=" * 50)

        @auto_track_publish("知乎")
        def publish_to_zhihu(content: dict) -> PublishResult:
            """模拟发布到知乎"""
            # 这里可以是实际的发布逻辑
            return PublishResult(
                success=True,
                title="测试发布文章",
                topic_id="TOPIC-2026-02-28-999",
                platform="知乎",
                account="CEO思考者",
                post_url="https://zhihu.com/p/test123",
                ai_score=0.15,
                word_count=3000,
                case_count=2
            )

        # 调用发布函数，装饰器会自动采集
        result = publish_to_zhihu({})
        print(f"发布结果: success={result.success}")

        # ====== 2. 查询功能示例 ======
        print("\n" + "=" * 50)
        print("2. 查询功能示例")
        print("=" * 50)

        # 按平台查询
        zhihu_records = query_by_platform("知乎")
        print(f"\n知乎发布记录数: {len(zhihu_records)}")
        for r in zhihu_records:
            print(f"  - {r.title} ({r.record_id})")

        # 按选题ID查询
        topic_records = query_by_topic_id("TOPIC-2026-02-28-001")
        print(f"\n选题 TOPIC-2026-02-28-001 的发布记录数: {len(topic_records)}")

        # 按日期查询
        today_records = query_by_date(datetime.now())
        print(f"\n今日发布记录数: {len(today_records)}")

        # 按日期范围查询
        week_records = query_by_date_range(
            start_date=datetime.now() - timedelta(days=7)
        )
        print(f"\n近7天发布记录数: {len(week_records)}")

        # ====== 3. 统计功能示例 ======
        print("\n" + "=" * 50)
        print("3. 统计功能示例")
        print("=" * 50)

        # 各平台发布数量
        platform_counts = count_by_platform()
        print(f"\n各平台发布数量:")
        for platform, count in platform_counts.items():
            print(f"  - {platform}: {count}")

        # 各平台详细统计
        platform_stats = count_by_platform_detailed()
        print(f"\n各平台详细统计:")
        for platform, stats in platform_stats.items():
            print(f"  - {platform}:")
            print(f"      发布数: {stats['count']}")
            print(f"      总字数: {stats['total_words']}")
            print(f"      总案例: {stats['total_cases']}")
            print(f"      平均AI评分: {stats['avg_ai_score']}")

        # 每日发布趋势
        trend = daily_trend(7)
        print(f"\n近7天发布趋势:")
        for date, count in trend.items():
            print(f"  - {date}: {count} 篇")

        # 详细趋势
        detailed_trend = daily_trend_detailed(3)
        print(f"\n近3天详细趋势:")
        for day in detailed_trend:
            print(f"  - {day['date']}: 共{day['total']}篇")
            for plat, cnt in day['by_platform'].items():
                print(f"      {plat}: {cnt}")

        # 统计摘要
        summary = get_statistics_summary()
        print(f"\n统计摘要:")
        print(f"  - 总发布数: {summary['total_published']}")
        print(f"  - 总失败数: {summary['total_failed']}")
        print(f"  - 总字数: {summary['total_words']}")
        print(f"  - 总案例: {summary['total_cases']}")
        print(f"  - 平均AI评分: {summary['avg_ai_score']}")
