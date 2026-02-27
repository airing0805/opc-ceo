# -*- coding: utf-8 -*-
"""
发布配置模块

提供统一的发布平台配置管理，支持多平台账号配置、发布设置和代理设置。

主要类:
    - PublisherConfig: 发布配置管理类
    - PlatformConfig: 平台配置数据类
    - PublishSettings: 发布设置数据类
    - ProxyConfig: 代理配置数据类
    - LoggingConfig: 日志配置数据类

快速使用:
    from config.publisher import PublisherConfig, get_publisher_config
    
    # 方式1: 创建实例
    config = PublisherConfig()
    
    # 方式2: 使用全局单例
    config = get_publisher_config()
    
    # 获取已启用平台
    platforms = config.get_enabled_platforms()
    
    # 获取平台 Cookies
    cookies = config.get_platform_cookies("zhihu")
"""

from config.publisher import (
    PublisherConfig,
    PlatformConfig,
    PublishSettings,
    ProxyConfig,
    LoggingConfig,
    get_publisher_config,
)

__all__ = [
    "PublisherConfig",
    "PlatformConfig", 
    "PublishSettings",
    "ProxyConfig",
    "LoggingConfig",
    "get_publisher_config",
]
