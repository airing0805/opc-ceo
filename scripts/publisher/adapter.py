"""
统一发布框架 - 适配器基类

提供平台适配器的通用实现
"""

import logging
from abc import ABC
from typing import Optional

from .base import (
    Platform,
    PlatformPublisher,
    Content,
    PublishResult,
    PostStatusResult,
    PostStatus,
)


logger = logging.getLogger(__name__)


class BaseAdapter(PlatformPublisher, ABC):
    """
    平台适配器基类
    
    提供通用的适配器实现，子类只需重写特定方法
    """
    
    def __init__(self):
        self._logged_in = False
        self._session = None
    
    @property
    def platform(self) -> Platform:
        """返回平台类型（子类必须重写）"""
        raise NotImplementedError
    
    @property
    def platform_name(self) -> str:
        """返回平台名称"""
        return self.platform.value
    
    def login(self) -> bool:
        """
        登录账号（子类可以重写具体实现）
        """
        logger.info(f"[{self.platform_name}] 开始登录...")
        # 子类实现具体的登录逻辑
        result = self._do_login()
        self._logged_in = result
        if result:
            logger.info(f"[{self.platform_name}] 登录成功")
        else:
            logger.warning(f"[{self.platform_name}] 登录失败")
        return result
    
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        return self._logged_in
    
    def publish(self, content: Content) -> PublishResult:
        """
        发布内容（通用实现）
        
        流程：
        1. 验证登录状态
        2. 验证内容
        3. 预处理内容
        4. 执行发布
        """
        # 检查登录状态
        if not self.is_logged_in():
            logger.warning(f"[{self.platform_name}] 未登录，尝试自动登录...")
            if not self.login():
                return PublishResult.failed_result(
                    f"发布失败：未登录且自动登录失败",
                    platform=self.platform
                )
        
        # 验证内容
        is_valid, error_msg = self.validate_content(content)
        if not is_valid:
            logger.warning(f"[{self.platform_name}] 内容验证失败: {error_msg}")
            return PublishResult.failed_result(
                f"内容验证失败: {error_msg}",
                platform=self.platform
            )
        
        # 预处理内容
        processed_content = self.preprocess_content(content)
        
        # 执行发布
        try:
            logger.info(f"[{self.platform_name}] 开始发布: {content.title}")
            result = self._do_publish(processed_content)
            if result.success:
                logger.info(f"[{self.platform_name}] 发布成功: {result.post_url}")
            else:
                logger.error(f"[{self.platform_name}] 发布失败: {result.error}")
            return result
        except Exception as e:
            logger.exception(f"[{self.platform_name}] 发布异常: {str(e)}")
            return PublishResult.failed_result(
                f"发布异常: {str(e)}",
                platform=self.platform
            )
    
    def get_status(self, post_id: str) -> PostStatusResult:
        """获取发布状态（子类可以重写具体实现）"""
        if not self.is_logged_in():
            return PostStatusResult(
                status=PostStatus.FAILED,
                post_id=post_id,
            )
        return self._do_get_status(post_id)
    
    # ========== 子类需要重写的方法 ==========
    
    def _do_login(self) -> bool:
        """
        执行具体的登录逻辑
        
        子类必须重写此方法
        """
        raise NotImplementedError(f"[{self.platform_name}] 子类必须实现 _do_login 方法")
    
    def _do_publish(self, content: Content) -> PublishResult:
        """
        执行具体的发布逻辑
        
        子类必须重写此方法
        """
        raise NotImplementedError(f"[{self.platform_name}] 子类必须实现 _do_publish 方法")
    
    def _do_get_status(self, post_id: str) -> PostStatusResult:
        """
        执行具体的状态查询逻辑
        
        子类可以重写此方法
        """
        raise NotImplementedError(f"[{self.platform_name}] 子类必须实现 _do_get_status 方法")
    
    # ========== 可选重写的方法 ==========
    
    def validate_content(self, content: Content) -> tuple[bool, str]:
        """
        验证内容是否符合平台要求
        
        子类可以重写此方法添加平台特定的验证
        """
        is_valid, msg = super().validate_content(content)
        if not is_valid:
            return is_valid, msg
        
        # 平台特定验证
        max_title_length = self._get_max_title_length()
        if len(content.title) > max_title_length:
            return False, f"标题长度超过平台限制({max_title_length}字符)"
        
        min_body_length = self._get_min_body_length()
        if len(content.body) < min_body_length:
            return False, f"正文长度低于平台要求({min_body_length}字符)"
        
        return True, ""
    
    def _get_max_title_length(self) -> int:
        """获取平台标题最大长度（子类可以重写）"""
        return 200
    
    def _get_min_body_length(self) -> int:
        """获取平台正文最小长度（子类可以重写）"""
        return 0
    
    def preprocess_content(self, content: Content) -> Content:
        """
        预处理内容
        
        子类可以重写此方法进行平台特定的预处理
        """
        return content


class LazyAdapter(BaseAdapter):
    """
    延迟加载适配器
    
    适用于需要时才初始化的平台
    """
    
    def __init__(self, adapter_class: type[BaseAdapter], **kwargs):
        super().__init__()
        self._adapter_class = adapter_class
        self._adapter_kwargs = kwargs
        self._adapter: Optional[BaseAdapter] = None
    
    def _get_adapter(self) -> BaseAdapter:
        """获取或创建实际适配器"""
        if self._adapter is None:
            self._adapter = self._adapter_class(**self._adapter_kwargs)
        return self._adapter
    
    @property
    def platform(self) -> Platform:
        return self._get_adapter().platform
    
    @property
    def platform_name(self) -> str:
        return self._get_adapter().platform_name
    
    def _do_login(self) -> bool:
        return self._get_adapter()._do_login()
    
    def _do_publish(self, content: Content) -> PublishResult:
        return self._get_adapter()._do_publish(content)
    
    def _do_get_status(self, post_id: str) -> PostStatusResult:
        return self._get_adapter()._do_get_status(post_id)
