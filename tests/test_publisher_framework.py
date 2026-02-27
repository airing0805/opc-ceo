# -*- coding: utf-8 -*-
"""
发布框架测试脚本

测试发布框架的以下功能：
1. 配置加载测试
2. 内容模型测试
3. 适配器接口测试
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.publisher import Content, PlatformPublisher, PublishResult, PostStatus
from scripts.publisher.base import PublisherRegistry, Platform
from config.publisher import get_publisher_config


class TestConfigLoading:
    """配置加载测试"""

    def test_get_publisher_config(self):
        """测试获取发布配置"""
        config = get_publisher_config()
        assert config is not None, "配置加载失败"
        print("[PASS] get_publisher_config")

    def test_get_enabled_platforms(self):
        """测试获取已启用平台"""
        config = get_publisher_config()
        platforms = config.get_enabled_platforms()
        assert isinstance(platforms, list), "平台列表应为列表类型"
        print(f"[PASS] get_enabled_platforms: {platforms}")

    def test_ai_detection_settings(self):
        """测试 AI 检测设置"""
        config = get_publisher_config()
        assert config.is_ai_detection_enabled() is not None
        assert config.get_ai_threshold() > 0
        print(f"[PASS] AI detection: {config.is_ai_detection_enabled()}, threshold: {config.get_ai_threshold()}")

    def test_publish_settings(self):
        """测试发布设置"""
        config = get_publisher_config()
        assert config.get_publish_interval() >= 0
        assert config.get_max_retries() >= 0
        assert config.get_timeout() > 0
        print(f"[PASS] publish_interval: {config.get_publish_interval()}, max_retries: {config.get_max_retries()}, timeout: {config.get_timeout()}")


class TestContentModel:
    """内容模型测试"""

    def test_content_creation(self):
        """测试内容创建"""
        content = Content(
            title="Test Title",
            body="Test body content",
            tags=["test", "ai"],
            category="tech",
            is_original=True
        )
        assert content.title == "Test Title"
        assert content.body == "Test body content"
        assert content.tags == ["test", "ai"]
        assert content.category == "tech"
        assert content.is_original is True
        print("[PASS] Content creation")

    def test_content_validation_valid(self):
        """测试内容验证 - 有效内容"""
        content = Content(title="Valid Title", body="Valid body content")
        assert content.validate() is True
        print("[PASS] Content validation - valid")

    def test_content_validation_empty_title(self):
        """测试内容验证 - 空标题"""
        content = Content(title="", body="Body content")
        assert content.validate() is False
        print("[PASS] Content validation - empty title")

    def test_content_validation_empty_body(self):
        """测试内容验证 - 空正文"""
        content = Content(title="Title", body="")
        assert content.validate() is False
        print("[PASS] Content validation - empty body")

    def test_content_validation_long_title(self):
        """测试内容验证 - 标题过长"""
        content = Content(title="A" * 201, body="Body content")
        assert content.validate() is False
        print("[PASS] Content validation - title too long")

    def test_to_platform_format(self):
        """测试平台格式转换"""
        content = Content(
            title="Test",
            body="Body",
            tags=["tag1"],
            category="cat1",
            cover_image="cover.jpg"
        )
        result = content.to_platform_format(Platform.ZHIHU)
        assert "title" in result
        assert "content" in result
        assert result["title"] == "Test"
        print("[PASS] to_platform_format")


class TestPublishResult:
    """发布结果测试"""

    def test_success_result(self):
        """测试成功结果创建"""
        result = PublishResult.success_result(
            post_id="12345",
            post_url="https://zhihu.com/p/12345",
            platform=Platform.ZHIHU
        )
        assert result.success is True
        assert result.post_id == "12345"
        assert result.post_url == "https://zhihu.com/p/12345"
        assert result.error == ""
        print("[PASS] success_result")

    def test_failed_result(self):
        """测试失败结果创建"""
        result = PublishResult.failed_result(
            error="Test error message",
            platform=Platform.ZHIHU
        )
        assert result.success is False
        assert result.post_id == ""
        assert result.post_url == ""
        assert result.error == "Test error message"
        print("[PASS] failed_result")


class TestPublisherRegistry:
    """发布器注册表测试"""

    def test_registry_register(self):
        """测试注册发布器"""
        # 创建一个测试发布器
        class TestPublisher(PlatformPublisher):
            @property
            def platform(self):
                return Platform.CUSTOM

            @property
            def platform_name(self):
                return "test"

            def publish(self, content):
                return PublishResult.success_result("1", "http://test.com")

            def get_status(self, post_id):
                return None

            def login(self):
                return True

            def is_logged_in(self):
                return False

        publisher = TestPublisher()
        PublisherRegistry.register(publisher)
        retrieved = PublisherRegistry.get(Platform.CUSTOM)
        assert retrieved is not None
        assert retrieved.platform == Platform.CUSTOM
        PublisherRegistry.unregister(Platform.CUSTOM)
        print("[PASS] registry register/unregister")

    def test_registry_get_all(self):
        """测试获取所有发布器"""
        publishers = PublisherRegistry.get_all()
        assert isinstance(publishers, dict)
        print(f"[PASS] registry get_all: {len(publishers)} publishers")


class TestPostStatus:
    """帖子状态枚举测试"""

    def test_post_status_values(self):
        """测试状态枚举值"""
        assert PostStatus.DRAFT.value == "draft"
        assert PostStatus.PENDING.value == "pending"
        assert PostStatus.PUBLISHED.value == "published"
        assert PostStatus.FAILED.value == "failed"
        assert PostStatus.DELETED.value == "deleted"
        print("[PASS] PostStatus enum values")


class TestPlatformEnum:
    """平台枚举测试"""

    def test_platform_values(self):
        """测试平台枚举值"""
        assert Platform.ZHIHU.value == "zhihu"
        assert Platform.CSDN.value == "csdn"
        assert Platform.JIANSHU.value == "jianshu"
        assert Platform.BILIBILI.value == "bilibili"
        assert Platform.TOUTIAO.value == "toutiao"
        assert Platform.CUSTOM.value == "custom"
        print("[PASS] Platform enum values")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Publisher Framework Test Suite")
    print("=" * 60)
    print()

    test_classes = [
        TestConfigLoading,
        TestContentModel,
        TestPublishResult,
        TestPublisherRegistry,
        TestPostStatus,
        TestPlatformEnum,
    ]

    total_passed = 0
    total_failed = 0

    for test_class in test_classes:
        print(f"\n--- {test_class.__name__} ---")
        instance = test_class()
        for method_name in dir(instance):
            if method_name.startswith("test_"):
                try:
                    getattr(instance, method_name)()
                    total_passed += 1
                except Exception as e:
                    print(f"[FAIL] {method_name}: {e}")
                    total_failed += 1

    print()
    print("=" * 60)
    print(f"Test Results: {total_passed} passed, {total_failed} failed")
    print("=" * 60)

    return total_failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
