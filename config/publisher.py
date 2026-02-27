# -*- coding: utf-8 -*-
"""
发布配置加载模块

提供统一的配置加载接口，支持 YAML 配置文件和环境变量。
敏感信息（如 Cookies）优先从环境变量读取。

Usage:
    from config.publisher import PublisherConfig
    
    config = PublisherConfig()
    zhihu_cookies = config.get_platform_cookies("zhihu")
    ai_enabled = config.is_ai_detection_enabled()
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    logging.warning("pyyaml 未安装，配置文件加载将受限")


# 环境变量映射
ENV_VAR_MAP = {
    # 知乎
    "zhihu": {
        "z_c0": "ZHIHU_COOKIE_Z_C0",
        "lg_id": "ZHIHU_COOKIE_LG_ID",
    },
    # CSDN
    "csdn": {
        "Cookie": "CSDN_COOKIE",
    },
    # 简书
    "jianshu": {
        "note_session": "JIANSHU_SESSION",
    },
    # 掘金
    "juejin": {
        "__guest": "JUEJIN_COOKIE",
    },
}

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent


@dataclass
class PlatformConfig:
    """平台配置"""
    enabled: bool = False
    cookies: Dict[str, str] = field(default_factory=dict)
    default_category: str = ""
    default_tags: List[str] = field(default_factory=list)


@dataclass
class PublishSettings:
    """发布设置"""
    enable_ai_detection: bool = True
    ai_threshold: int = 60
    add_watermark: bool = False
    publish_interval: int = 300
    max_retries: int = 3
    timeout: int = 30


@dataclass
class ProxyConfig:
    """代理配置"""
    enabled: bool = False
    http: str = ""
    https: str = ""


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    file_enabled: bool = True
    file_path: str = "logs/publisher.log"


class PublisherConfig:
    """
    发布配置管理类
    
    统一管理各平台发布配置，支持从 YAML 文件和环境变量加载配置。
    敏感信息（Cookies）优先从环境变量读取。
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置
        
        Args:
            config_path: 配置文件路径，默认为 config/publisher_config.yaml
        """
        self._config_path = config_path or str(PROJECT_ROOT / "config" / "publisher_config.yaml")
        self._config: Dict[str, Any] = {}
        self._platforms: Dict[str, PlatformConfig] = {}
        self._publish_settings: PublishSettings = PublishSettings()
        self._proxy: ProxyConfig = ProxyConfig()
        self._logging: LoggingConfig = LoggingConfig()
        
        self._load_config()
    
    def _load_config(self) -> None:
        """加载配置文件"""
        config_file = Path(self._config_path)

        if not config_file.exists():
            logging.warning(f"配置文件不存在: {self._config_path}，使用默认配置")
            self._use_defaults()
            return

        if not YAML_AVAILABLE:
            logging.warning("pyyaml 未安装，无法解析配置文件，使用默认配置")
            self._use_defaults()
            return

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            logging.error(f"配置文件解析失败: {e}，使用默认配置")
            self._use_defaults()
            return

        self._parse_platforms()
        self._parse_publish_settings()
        self._parse_proxy()
        self._parse_logging()
    
    def _use_defaults(self) -> None:
        """使用默认配置"""
        self._platforms = {}
        self._publish_settings = PublishSettings()
        self._proxy = ProxyConfig()
        self._logging = LoggingConfig()
    
    def _parse_platforms(self) -> None:
        """解析平台配置"""
        platforms_data = self._config.get("platforms", {})
        
        for platform_name, platform_data in platforms_data.items():
            cookies = platform_data.get("cookies", {})
            
            # 从环境变量覆盖敏感信息
            env_map = ENV_VAR_MAP.get(platform_name, {})
            for cookie_key, env_var in env_map.items():
                env_value = os.environ.get(env_var)
                if env_value:
                    cookies[cookie_key] = env_value
            
            self._platforms[platform_name] = PlatformConfig(
                enabled=platform_data.get("enabled", False),
                cookies=cookies,
                default_category=platform_data.get("default_category", ""),
                default_tags=platform_data.get("default_tags", []),
            )
    
    def _parse_publish_settings(self) -> None:
        """解析发布设置"""
        settings = self._config.get("publish_settings", {})
        self._publish_settings = PublishSettings(
            enable_ai_detection=settings.get("enable_ai_detection", True),
            ai_threshold=settings.get("ai_threshold", 60),
            add_watermark=settings.get("add_watermark", False),
            publish_interval=settings.get("publish_interval", 300),
            max_retries=settings.get("max_retries", 3),
            timeout=settings.get("timeout", 30),
        )
    
    def _parse_proxy(self) -> None:
        """解析代理配置"""
        proxy = self._config.get("proxy", {})
        self._proxy = ProxyConfig(
            enabled=proxy.get("enabled", False),
            http=proxy.get("http", ""),
            https=proxy.get("https", ""),
        )
    
    def _parse_logging(self) -> None:
        """解析日志配置"""
        logging_config = self._config.get("logging", {})
        self._logging = LoggingConfig(
            level=logging_config.get("level", "INFO"),
            file_enabled=logging_config.get("file_enabled", True),
            file_path=logging_config.get("file_path", "logs/publisher.log"),
        )
    
    # ==================== 公共接口 ====================
    
    def get_platform(self, platform_name: str) -> Optional[PlatformConfig]:
        """
        获取指定平台配置
        
        Args:
            platform_name: 平台名称 (zhihu, csdn, jianshu, juejin)
            
        Returns:
            平台配置对象，如果平台不存在或未启用返回 None
        """
        return self._platforms.get(platform_name)
    
    def get_enabled_platforms(self) -> List[str]:
        """
        获取所有已启用的平台列表
        
        Returns:
            已启用的平台名称列表
        """
        return [
            name for name, config in self._platforms.items()
            if config.enabled
        ]
    
    def get_platform_cookies(self, platform_name: str) -> Dict[str, str]:
        """
        获取平台 Cookies
        
        Args:
            platform_name: 平台名称
            
        Returns:
            Cookies 字典
        """
        platform = self._platforms.get(platform_name)
        if platform:
            return platform.cookies
        return {}
    
    def get_platform_category(self, platform_name: str) -> str:
        """
        获取平台默认分类
        
        Args:
            platform_name: 平台名称
            
        Returns:
            默认分类名称
        """
        platform = self._platforms.get(platform_name)
        if platform:
            return platform.default_category
        return ""
    
    def get_platform_tags(self, platform_name: str) -> List[str]:
        """
        获取平台默认标签
        
        Args:
            platform_name: 平台名称
            
        Returns:
            默认标签列表
        """
        platform = self._platforms.get(platform_name)
        if platform:
            return platform.default_tags
        return []
    
    def is_ai_detection_enabled(self) -> bool:
        """是否启用 AI 检测"""
        return self._publish_settings.enable_ai_detection
    
    def get_ai_threshold(self) -> int:
        """获取 AI 阈值"""
        return self._publish_settings.ai_threshold
    
    def is_watermark_enabled(self) -> bool:
        """是否启用水印"""
        return self._publish_settings.add_watermark
    
    def get_publish_interval(self) -> int:
        """获取发布间隔（ get_publish_interval秒）"""
        return self._publish_settings.publish_interval
    
    def get_max_retries(self) -> int:
        """获取最大重试次数"""
        return self._publish_settings.max_retries
    
    def get_timeout(self) -> int:
        """获取超时时间（秒）"""
        return self._publish_settings.timeout
    
    def is_proxy_enabled(self) -> bool:
        """是否启用代理"""
        return self._proxy.enabled
    
    def get_proxy(self) -> Dict[str, str]:
        """获取代理配置"""
        return {
            "http": self._proxy.http,
            "https": self._proxy.https,
        }
    
    def get_logging_level(self) -> str:
        """获取日志级别"""
        return self._logging.level
    
    def is_file_logging_enabled(self) -> bool:
        """是否启用文件日志"""
        return self._logging.file_enabled
    
    def get_log_file_path(self) -> str:
        """获取日志文件路径"""
        return self._logging.file_path
    
    def reload(self) -> None:
        """重新加载配置"""
        self._load_config()


# 全局配置实例
_default_config: Optional[PublisherConfig] = None


def get_publisher_config() -> PublisherConfig:
    """
    获取全局发布配置实例（单例模式）
    
    Returns:
        PublisherConfig 实例
    """
    global _default_config
    if _default_config is None:
        _default_config = PublisherConfig()
    return _default_config
