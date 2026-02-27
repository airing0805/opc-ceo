# -*- coding: utf-8 -*-
"""
统一发布器 - 整合检测+发布+采集

功能：
1. AI检测 - 发布前自动检测AI味分数
2. 平台发布 - 支持多平台统一发布
3. 自动采集 - 发布成功后自动记录到知识图谱

使用示例：
    from scripts.publisher.publisher import UnifiedPublisher, PublisherConfig

    # 创建配置
    config = PublisherConfig(
        enable_ai_detection=True,
        ai_threshold=60,
        default_platform="zhihu"
    )

    # 创建发布器
    publisher = UnifiedPublisher(config)

    # 发布内容
    content = Content(
        title="测试文章",
        body="文章内容...",
        tags=["AI", "创业"],
        topic_id="TOPIC-2026-02-28-001"
    )

    result = publisher.publish(content, "zhihu")
    print(result)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from .base import (
    Platform,
    PlatformPublisher,
    Content,
    PublishResult as BasePublishResult,
    PostStatus,
)
from .tracker import (
    create_publish_record,
    save_to_memory,
    PostStatus as TrackerPostStatus,
)
from scripts.ai_detector import detect_ai_score, AIDetector


# ============================================================
# 配置类
# ============================================================


@dataclass
class PublisherConfig:
    """发布器配置"""

    # AI检测配置
    enable_ai_detection: bool = True      # 是否启用AI检测
    ai_threshold: float = 60.0             # AI味阈值 (0-100)

    # 默认平台配置
    default_platform: str = "zhihu"         # 默认发布平台

    # 自动采集配置
    enable_auto_track: bool = True         # 是否启用自动采集
    default_account: str = "CEO思考者"     # 默认账号

    # 发布配置
    enable_auto_login: bool = True         # 是否自动登录

    def is_ai_detection_enabled(self) -> bool:
        """检查是否启用AI检测"""
        return self.enable_ai_detection

    def get_ai_threshold(self) -> float:
        """获取AI阈值"""
        return self.ai_threshold

    def should_auto_track(self) -> bool:
        """检查是否启用自动采集"""
        return self.enable_auto_track


# ============================================================
# 统一发布器
# ============================================================


class UnifiedPublisher:
    """
    统一发布器 - 整合检测+发布+采集

    核心流程：
    1. AI检测（可选）- 发布前检测AI味分数
    2. 平台发布 - 调用对应平台发布器
    3. 自动采集（可选）- 发布成功后记录到知识图谱
    """

    def __init__(self, config: PublisherConfig):
        """
        初始化统一发布器

        Args:
            config: 发布器配置
        """
        self.config = config
        self._publishers: Dict[str, PlatformPublisher] = {}
        self._ai_detector = AIDetector()

    def register_publisher(self, publisher: PlatformPublisher) -> None:
        """
        注册平台发布器

        Args:
            publisher: 平台发布器实例
        """
        self._publishers[publisher.platform_name] = publisher

    def get_publisher(self, platform: str) -> Optional[PlatformPublisher]:
        """
        获取平台发布器

        Args:
            platform: 平台名称

        Returns:
            PlatformPublisher 或 None
        """
        publisher = self._publishers.get(platform)
        if publisher is None:
            # 尝试按枚举值查找
            try:
                platform_enum = Platform(platform)
                publisher = self._publishers.get(platform_enum.value)
            except ValueError:
                pass
        return publisher

    def publish(
        self,
        content: Content,
        platform: str,
        account: Optional[str] = None,
    ) -> BasePublishResult:
        """
        发布内容到指定平台（自动检测+自动采集）

        流程：
        1. AI检测（如果启用）
        2. 平台发布
        3. 自动采集（如果发布成功）

        Args:
            content: 要发布的内容
            platform: 目标平台（如 "zhihu", "jianshu"）
            account: 发布账号（可选，默认使用配置中的账号）

        Returns:
            PublishResult: 发布结果
        """
        # 使用指定账号或默认账号
        publish_account = account or self.config.default_account

        # ========== 1. AI检测 ==========
        ai_score = 0.0
        if self.config.is_ai_detection_enabled():
            ai_score = detect_ai_score(content.body)
            if ai_score > self.config.get_ai_threshold():
                return BasePublishResult.failed_result(
                    f"AI味检测未通过 ({ai_score:.1f}分 > {self.config.get_ai_threshold()}分)",
                    platform=self._get_platform_enum(platform)
                )

        # ========== 2. 获取发布器 ==========
        publisher = self.get_publisher(platform)
        if publisher is None:
            return BasePublishResult.failed_result(
                f"未找到平台发布器: {platform}",
                platform=self._get_platform_enum(platform)
            )

        # 检查登录状态
        if not publisher.is_logged_in():
            if self.config.enable_auto_login:
                publisher.login()
            else:
                return BasePublishResult.failed_result(
                    f"未登录: {platform}",
                    platform=self._get_platform_enum(platform)
                )

        # ========== 3. 执行发布 ==========
        result = publisher.publish(content)

        # ========== 4. 自动采集 ==========
        if result.success and self.config.should_auto_track():
            self._auto_track(
                content=content,
                platform=platform,
                account=publish_account,
                ai_score=ai_score,
                post_url=result.post_url,
            )

        return result

    def publish_multi(
        self,
        content: Content,
        platforms: List[str],
    ) -> Dict[str, BasePublishResult]:
        """
        发布内容到多个平台

        Args:
            content: 要发布的内容
            platforms: 目标平台列表

        Returns:
            Dict[str, PublishResult]: 各平台的发布结果
        """
        results = {}
        for platform in platforms:
            result = self.publish(content, platform)
            results[platform] = result
        return results

    def _auto_track(
        self,
        content: Content,
        platform: str,
        account: str,
        ai_score: float,
        post_url: Optional[str] = None,
    ) -> None:
        """
        自动采集发布记录

        Args:
            content: 发布的内容
            platform: 发布平台
            account: 发布账号
            ai_score: AI味分数
            post_url: 文章链接
        """
        try:
            # 创建发布记录
            record = create_publish_record(
                title=content.title,
                topic_id=content.topic_id,
                platform=platform,
                account=account,
                ai_score=ai_score,
                word_count=len(content.body),
                case_count=content.case_count,
                post_url=post_url,
                status=TrackerPostStatus.PUBLISHED,
            )

            # 保存到知识图谱
            save_to_memory(record)

            print(f"[自动采集] 已记录发布: {content.title} -> {platform}")

        except Exception as e:
            print(f"[自动采集] 记录失败: {e}")

    def _get_platform_enum(self, platform: str) -> Platform:
        """获取平台枚举"""
        try:
            return Platform(platform)
        except ValueError:
            return Platform.CUSTOM

    def get_statistics(self) -> Dict:
        """
        获取发布统计数据

        Returns:
            Dict: 统计数据
        """
        from .tracker import get_statistics_summary
        return get_statistics_summary()


# ============================================================
# 便捷函数
# ============================================================


def create_unified_publisher(
    enable_ai_detection: bool = True,
    ai_threshold: float = 60.0,
    enable_auto_track: bool = True,
) -> UnifiedPublisher:
    """
    创建统一发布器的便捷函数

    Args:
        enable_ai_detection: 是否启用AI检测
        ai_threshold: AI味阈值
        enable_auto_track: 是否启用自动采集

    Returns:
        UnifiedPublisher: 配置好的统一发布器
    """
    config = PublisherConfig(
        enable_ai_detection=enable_ai_detection,
        ai_threshold=ai_threshold,
        enable_auto_track=enable_auto_track,
    )
    return UnifiedPublisher(config)


# ============================================================
# 使用示例
# ============================================================


def demo_with_adapter():
    """
    示例：注册平台适配器并发布

    这个示例展示了完整的发布流程：
    1. 创建配置
    2. 注册平台适配器
    3. 发布内容
    """
    from scripts.publisher.zhihu import ZhihuAdapter
    from scripts.publisher.base import Platform

    # 1. 创建配置
    config = PublisherConfig(
        enable_ai_detection=True,      # 启用AI检测
        ai_threshold=60.0,             # AI味阈值60分
        default_platform="zhihu",
        enable_auto_track=True,        # 启用自动采集
        default_account="CEO思考者",
    )

    # 2. 创建发布器
    publisher = UnifiedPublisher(config)

    # 3. 注册平台适配器
    zhihu_adapter = ZhihuAdapter()
    publisher.register_publisher(zhihu_adapter)

    # 4. 创建内容
    content = Content(
        title="一人公司CEO的时间管理秘诀",
        body="""
# 时间管理对于一人公司CEO的重要性

作为一人公司的CEO，时间是最稀缺的资源。如何在有限的时间内完成更多的工作，是每个CEO都必须面对的问题。

## 核心原则

1. **优先级排序** - 每天先做最重要的三件事
2. **批量处理** - 集中处理同类任务
3. **自动化** - 让工具代替人工

## 实践方法

首先，要学会说"不"。其次，要善于委托。最后，要持续优化。

总之，时间管理是一门需要不断实践的艺术。
        """,
        tags=["时间管理", "CEO", "效率"],
        category="创业",
        topic_id="TOPIC-2026-02-28-001",
        case_count=3,
    )

    # 5. 发布（注意：需要先登录）
    # result = publisher.publish(content, "zhihu")
    # print(f"发布结果: {result.success}")
    # if result.success:
    #     print(f"文章链接: {result.post_url}")

    print("发布器已配置完成，可以调用 publish() 发布内容")
    return publisher


def demo_ai_detection_only():
    """示例：仅测试AI检测功能"""
    # 测试内容
    test_text = """
首先，我们需要明确目标。其次，要制定详细的计划。最后，要坚持执行。

总的来说，时间管理对于一人公司CEO来说非常重要。

除此之外，还需要注意以下几点：

1. 首先要学会优先级排序
2. 其次要善于委托
3. 最后要持续优化流程
    """

    # 检测AI味
    score = detect_ai_score(test_text)
    print(f"AI味分数: {score:.1f}")

    if score >= 60:
        print("高AI味 - 需要修改")
    elif score >= 40:
        print("中AI味 - 建议优化")
    else:
        print("低AI味 - 通过")

    return score


if __name__ == "__main__":
    print("=" * 60)
    print("1. 统一发布器示例")
    print("=" * 60)

    # 创建配置
    config = PublisherConfig(
        enable_ai_detection=True,
        ai_threshold=60.0,
        default_platform="zhihu",
        enable_auto_track=True,
        default_account="CEO思考者",
    )

    # 创建发布器
    publisher = UnifiedPublisher(config)

    # 创建内容
    content = Content(
        title="一人公司CEO的时间管理秘诀",
        body="""
# 时间管理对于一人公司CEO的重要性

作为一人公司的CEO，时间是最稀缺的资源。

## 核心原则

1. 优先级排序
2. 批量处理
3. 自动化

## 实践方法

首先，要学会说"不"。其次，要善于委托。最后，要持续优化。

总之，时间管理是一门需要不断实践的艺术。
        """,
        tags=["时间管理", "CEO", "效率"],
        category="创业",
        topic_id="TOPIC-2026-02-28-001",
        case_count=3,
    )

    # 打印AI检测结果
    if config.is_ai_detection_enabled():
        ai_score = detect_ai_score(content.body)
        print(f"\nAI味分数: {ai_score:.1f}")
        if ai_score > config.get_ai_threshold():
            print(f"警告: AI味分数超过阈值 ({ai_score:.1f} > {config.get_ai_threshold()})")
        else:
            print("AI味检测通过")

    print("\n" + "=" * 60)
    print("2. AI检测单独测试")
    print("=" * 60)
    demo_ai_detection_only()

    print("\n" + "=" * 60)
    print("3. 完整使用示例（需要平台适配器）")
    print("=" * 60)
    demo_with_adapter()
