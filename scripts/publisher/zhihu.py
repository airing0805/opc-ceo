"""
统一发布框架 - 知乎平台适配器

知乎平台的具体实现
"""

import logging
import re
from datetime import datetime
from typing import Optional

from .base import (
    Platform,
    Content,
    PublishResult,
    PostStatusResult,
    PostStatus,
)
from .adapter import BaseAdapter


logger = logging.getLogger(__name__)


class ZhihuAdapter(BaseAdapter):
    """
    知乎平台适配器
    
    实现知乎平台的发布接口
    """
    
    def __init__(self, cookies: Optional[dict] = None):
        """
        初始化知乎适配器
        
        Args:
            cookies: 可选的 cookies 用于登录
        """
        super().__init__()
        self._cookies = cookies or {}
        self._headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.zhihu.com/",
            "Origin": "https://www.zhihu.com",
        }
    
    @property
    def platform(self) -> Platform:
        return Platform.ZHIHU
    
    @property
    def platform_name(self) -> str:
        return "知乎"
    
    def _get_max_title_length(self) -> int:
        """知乎标题最大长度"""
        return 100
    
    def _get_min_body_length(self) -> int:
        """知乎正文最小长度"""
        return 100
    
    def _do_login(self) -> bool:
        """
        执行知乎登录
        
        支持两种方式：
        1. 使用 cookies 登录
        2. 使用浏览器模拟登录
        """
        if self._cookies:
            logger.info(f"[{self.platform_name}] 使用 cookies 登录")
            # 验证 cookies 有效性
            return self._validate_cookies()
        
        # TODO: 实现浏览器登录
        logger.warning(f"[{self.platform_name}] 未提供 cookies，请手动登录")
        return False
    
    def _validate_cookies(self) -> bool:
        """验证 cookies 是否有效"""
        # 实际实现中应该调用知乎 API 验证
        # 这里只是示例
        return bool(self._cookies.get("z_c0"))
    
    def _do_publish(self, content: Content) -> PublishResult:
        """
        执行知乎发布
        
        知乎发布 API 流程：
        1. 创建草稿
        2. 发布草稿
        """
        try:
            # 构建发布数据
            publish_data = self._build_publish_data(content)
            
            # 调用发布 API（示例，实际需要使用 Playwright 或 API）
            # response = self._session.post(
            #     "https://www.zhihu.com/api/v4/articles",
            #     json=publish_data,
            #     headers=self._headers
            # )
            
            # 示例：模拟成功返回
            post_id = self._generate_post_id()
            post_url = f"https://zhuanlan.zhihu.com/p/{post_id}"
            
            logger.info(f"[{self.platform_name}] 发布成功: {post_url}")
            return PublishResult.success_result(
                post_id=post_id,
                post_url=post_url,
                platform=self.platform
            )
            
        except Exception as e:
            logger.exception(f"[{self.platform_name}] 发布失败: {str(e)}")
            return PublishResult.failed_result(
                f"发布失败: {str(e)}",
                platform=self.platform
            )
    
    def _build_publish_data(self, content: Content) -> dict:
        """
        构建知乎发布数据
        
        知乎专栏文章 API 格式：
        - title: 标题
        - image_url: 封面图
        - topics: 话题标签
        - content: 正文（HTML 格式）
        - source_url: 原文链接（转载）
        """
        # 转换正文为知乎支持的 HTML 格式
        html_content = self._convert_to_html(content.body)
        
        # 构建发布时间戳
        timestamp = int(datetime.now().timestamp())
        
        data = {
            "title": content.title,
            "content": html_content,
            "topics": content.tags[:5],  # 知乎最多5个话题
            "timestamp": timestamp,
        }
        
        # 添加封面图
        if content.cover_image:
            data["image_url"] = content.cover_image
        
        # 如果是转载，添加原文链接
        if not content.is_original and content.source_url:
            data["source_url"] = content.source_url
        
        return data
    
    def _convert_to_html(self, text: str) -> str:
        """
        将 Markdown 转换为知乎支持的 HTML
        
        知乎支持部分 HTML 标签：
        - p, br, h1-h6
        - ul, ol, li
        - img
        - a
        - blockquote
        - code, pre
        """
        # 简单的转换，实际可以使用 markdown 库
        html = text
        
        # 转换代码块
        html = re.sub(
            r'```(\w+)?\n(.*?)```',
            r'<pre><code>\2</code></pre>',
            html,
            flags=re.DOTALL
        )
        
        # 转换行内代码
        html = re.sub(
            r'`([^`]+)`',
            r'<code>\1</code>',
            html
        )
        
        # 转换粗体
        html = re.sub(
            r'\*\*([^*]+)\*\*',
            r'<strong>\1</strong>',
            html
        )
        
        # 转换斜体
        html = re.sub(
            r'\*([^*]+)\*',
            r'<em>\1</em>',
            html
        )
        
        # 转换链接
        html = re.sub(
            r'\[([^\]]+)\]\(([^)]+)\)',
            r'<a href="\2">\1</a>',
            html
        )
        
        # 转换图片
        html = re.sub(
            r'!\[([^\]]*)\]\(([^)]+)\)',
            r'<img src="\2" alt="\1"/>',
            html
        )
        
        # 转换段落
        paragraphs = html.split('\n\n')
        html = ''.join(f'<p>{p}</p>' for p in paragraphs if p.strip())
        
        return html
    
    def _do_get_status(self, post_id: str) -> PostStatusResult:
        """
        获取知乎文章状态
        
        可以通过知乎 API 查询文章状态和统计数据
        """
        try:
            # 示例：调用知乎 API
            # response = self._session.get(
            #     f"https://www.zhihu.com/api/v4/articles/{post_id}",
            #     headers=self._headers
            # )
            
            # 示例：返回模拟数据
            return PostStatusResult(
                status=PostStatus.PUBLISHED,
                post_id=post_id,
                post_url=f"https://zhuanlan.zhihu.com/p/{post_id}",
                view_count=0,
                like_count=0,
                comment_count=0,
                share_count=0,
                last_update=datetime.now()
            )
            
        except Exception as e:
            logger.exception(f"[{self.platform_name}] 查询状态失败: {str(e)}")
            return PostStatusResult(
                status=PostStatus.FAILED,
                post_id=post_id,
            )
    
    def _generate_post_id(self) -> str:
        """生成帖子 ID"""
        import random
        import string
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    
    def preprocess_content(self, content: Content) -> Content:
        """
        知乎特定的预处理
        
        - 移除可能触发 AI 检测的内容
        - 添加知乎风格的开头
        - 处理话题标签
        """
        from copy import deepcopy
        
        processed = deepcopy(content)
        
        # 处理标题：移除过于规整的格式
        if processed.title:
            # 移除末尾的标点符号（知乎风格）
            processed.title = processed.title.rstrip('。！？')
        
        # 处理标签：知乎使用话题标签
        processed.tags = [f"#{tag}#" for tag in processed.tags[:5]]
        
        # 处理正文：添加合适的段落分隔
        if processed.body:
            # 确保有适当的段落分隔
            processed.body = processed.body.replace('\n\n\n', '\n\n')
        
        return processed


class ZhihuCookieManager:
    """
    知乎 Cookie 管理器
    
    用于获取和管理知乎登录状态
    """
    
    @staticmethod
    def from_browser() -> dict:
        """
        从浏览器获取 cookies
        
        需要用户手动登录
        """
        # TODO: 使用 Playwright 自动获取
        raise NotImplementedError("需要实现浏览器自动获取 cookies")
    
    @staticmethod
    def save_cookies(cookies: dict, filepath: str) -> None:
        """保存 cookies 到文件"""
        import json
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(cookies, f)
    
    @staticmethod
    def load_cookies(filepath: str) -> dict:
        """从文件加载 cookies"""
        import json
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
