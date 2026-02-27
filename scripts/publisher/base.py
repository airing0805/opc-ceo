"""
统一发布框架 - 基础接口定义

定义多平台发布的标准接口和数据模型
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class PostStatus(Enum):
    """帖子状态枚举"""
    DRAFT = "draft"           # 草稿
    PENDING = "pending"       # 待发布
    PUBLISHED = "published"   # 已发布
    FAILED = "failed"         # 发布失败
    DELETED = "deleted"       # 已删除


class Platform(Enum):
    """支持的平台枚举"""
    ZHIHU = "zhihu"
    CSDN = "csdn"
    JIANSHU = "jianshu"
    BILIBILI = "bilibili"
    TOUTIAO = "toutiao"
    CUSTOM = "custom"


@dataclass
class Content:
    """内容数据模型"""
    title: str                           # 标题
    body: str                            # 正文
    tags: List[str] = field(default_factory=list)  # 标签
    category: str = ""                   # 分类
    cover_image: Optional[str] = None    # 封面图（可选）
    summary: str = ""                    # 摘要（可选）
    author: str = ""                     # 作者
    source_url: str = ""                 # 原文链接（转载时使用）
    is_original: bool = True            # 是否原创
    topic_id: str = ""                   # 选题ID（扩展字段）
    case_count: int = 0                  # 案例数量（扩展字段）
    
    def validate(self) -> bool:
        """验证内容是否符合发布要求"""
        if not self.title or len(self.title.strip()) == 0:
            return False
        if not self.body or len(self.body.strip()) == 0:
            return False
        if len(self.title) > 200:
            return False
        return True
    
    def to_platform_format(self, platform: Platform) -> dict:
        """转换为特定平台的格式"""
        # 子类可以重写此方法进行平台特定转换
        return {
            "title": self.title,
            "content": self.body,
            "tags": self.tags,
            "category": self.category,
            "cover": self.cover_image,
        }


@dataclass
class PublishResult:
    """发布结果模型"""
    success: bool                        # 是否成功
    post_id: str = ""                   # 平台返回的ID
    post_url: str = ""                  # 帖子链接
    error: str = ""                      # 错误信息（失败时）
    timestamp: datetime = field(default_factory=datetime.now)  # 发布时间
    platform: Platform = Platform.CUSTOM # 发布的平台
    
    @classmethod
    def success_result(cls, post_id: str, post_url: str, platform: Platform = Platform.CUSTOM) -> 'PublishResult':
        """创建成功结果"""
        return cls(
            success=True,
            post_id=post_id,
            post_url=post_url,
            platform=platform,
            timestamp=datetime.now()
        )
    
    @classmethod
    def failed_result(cls, error: str, platform: Platform = Platform.CUSTOM) -> 'PublishResult':
        """创建失败结果"""
        return cls(
            success=False,
            error=error,
            platform=platform,
            timestamp=datetime.now()
        )


@dataclass
class PostStatusResult:
    """帖子状态查询结果"""
    status: PostStatus                  # 状态
    post_id: str                        # 帖子ID
    post_url: str = ""                  # 帖子链接
    view_count: int = 0                 # 阅读数
    like_count: int = 0                 # 点赞数
    comment_count: int = 0              # 评论数
    share_count: int = 0                # 分享数
    last_update: datetime = field(default_factory=datetime.now)  # 最后更新时间


class PlatformPublisher(ABC):
    """
    平台发布器抽象基类
    
    所有平台适配器必须实现此接口
    """
    
    @property
    @abstractmethod
    def platform(self) -> Platform:
        """返回平台类型"""
        pass
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """返回平台名称（用于日志等）"""
        pass
    
    @abstractmethod
    def publish(self, content: Content) -> PublishResult:
        """
        发布内容
        
        Args:
            content: 要发布的内容
            
        Returns:
            PublishResult: 发布结果
        """
        pass
    
    @abstractmethod
    def get_status(self, post_id: str) -> PostStatusResult:
        """
        获取发布状态
        
        Args:
            post_id: 帖子ID
            
        Returns:
            PostStatusResult: 状态查询结果
        """
        pass
    
    @abstractmethod
    def login(self) -> bool:
        """
        登录账号
        
        Returns:
            bool: 登录是否成功
        """
        pass
    
    @abstractmethod
    def is_logged_in(self) -> bool:
        """
        检查是否已登录
        
        Returns:
            bool: 是否已登录
        """
        pass
    
    def validate_content(self, content: Content) -> tuple[bool, str]:
        """
        验证内容是否符合平台要求
        
        Args:
            content: 要验证的内容
            
        Returns:
            tuple[bool, str]: (是否有效, 错误信息)
        """
        if not content.validate():
            return False, "内容验证失败：标题或正文不能为空"
        
        # 平台特定验证（子类可以重写）
        return True, ""
    
    def preprocess_content(self, content: Content) -> Content:
        """
        预处理内容（子类可以重写）
        
        例如：添加平台特定的水印、调整格式等
        """
        return content


class PublisherRegistry:
    """
    发布器注册表
    
    用于管理所有平台发布器
    """
    
    _publishers: dict[Platform, PlatformPublisher] = {}
    
    @classmethod
    def register(cls, publisher: PlatformPublisher) -> None:
        """注册发布器"""
        cls._publishers[publisher.platform] = publisher
    
    @classmethod
    def get(cls, platform: Platform) -> Optional[PlatformPublisher]:
        """获取发布器"""
        return cls._publishers.get(platform)
    
    @classmethod
    def get_all(cls) -> dict[Platform, PlatformPublisher]:
        """获取所有已注册的发布器"""
        return cls._publishers.copy()
    
    @classmethod
    def unregister(cls, platform: Platform) -> None:
        """注销发布器"""
        cls._publishers.pop(platform, None)
