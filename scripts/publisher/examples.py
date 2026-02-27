"""
统一发布框架 - 使用示例

展示如何使用发布框架进行多平台发布
"""

from datetime import datetime
from scripts.publisher import (
    PlatformPublisher,
    Content,
    PublishResult,
    Platform,
    PublisherRegistry,
    ZhihuAdapter,
)


def example_basic_usage():
    """基础使用示例"""
    
    # 1. 创建内容
    content = Content(
        title="测试文章标题",
        body="这是文章的正文内容...\n\n## 第二段\n\n更多内容",
        tags=["Python", "编程", "技术"],
        category="技术",
        cover_image="https://example.com/cover.jpg",
        is_original=True,
    )
    
    # 2. 创建知乎适配器
    zhihu = ZhihuAdapter()
    
    # 3. 登录
    if zhihu.login():
        print("登录成功")
    
    # 4. 发布
    result = zhihu.publish(content)
    if result.success:
        print(f"发布成功: {result.post_url}")
    else:
        print(f"发布失败: {result.error}")


def example_with_registry():
    """使用注册表发布到多个平台"""
    
    # 注册适配器
    PublisherRegistry.register(ZhihuAdapter())
    # PublisherRegistry.register(CsdnAdapter())
    # PublisherRegistry.register(JianshuAdapter())
    
    # 创建内容
    content = Content(
        title="一篇多平台发布的文章",
        body="这是文章内容...",
        tags=["技术", "分享"],
        category="科技",
    )
    
    # 发布到所有已注册平台
    results = {}
    for platform, publisher in PublisherRegistry.get_all().items():
        result = publisher.publish(content)
        results[platform.value] = result


def example_validate_content():
    """验证内容示例"""
    
    content = Content(
        title="",
        body="内容",
    )
    
    zhihu = ZhihuAdapter()
    is_valid, msg = zhihu.validate_content(content)
    print(f"验证结果: {is_valid}, 消息: {msg}")


if __name__ == "__main__":
    example_basic_usage()
