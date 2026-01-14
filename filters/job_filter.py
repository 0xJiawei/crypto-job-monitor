"""
职位过滤器

根据配置的关键词过滤职位，只保留目标类型的岗位。
"""
import re
import logging
from typing import Optional

from scrapers.base import Job
import config

logger = logging.getLogger(__name__)


class JobFilter:
    """职位过滤器"""
    
    def __init__(
        self,
        include_keywords: Optional[list[str]] = None,
        exclude_keywords: Optional[list[str]] = None
    ):
        """
        初始化过滤器
        
        Args:
            include_keywords: 包含关键词列表（默认使用配置）
            exclude_keywords: 排除关键词列表（默认使用配置）
        """
        self.include_keywords = include_keywords or config.INCLUDE_KEYWORDS
        self.exclude_keywords = exclude_keywords or config.EXCLUDE_KEYWORDS
        
        # 预编译正则表达式以提高性能
        self._include_patterns = self._compile_patterns(self.include_keywords)
        self._exclude_patterns = self._compile_patterns(self.exclude_keywords)
    
    def _compile_patterns(self, keywords: list[str]) -> list[re.Pattern]:
        """将关键词编译为正则表达式"""
        patterns = []
        for keyword in keywords:
            # 转义特殊字符，并添加单词边界
            escaped = re.escape(keyword.strip())
            # 使用 \b 确保是完整单词匹配（对于短词如 "bd"）
            pattern = re.compile(rf'\b{escaped}\b', re.IGNORECASE)
            patterns.append(pattern)
        return patterns
    
    def should_include(self, job: Job) -> bool:
        """
        判断职位是否应该被包含
        
        Args:
            job: Job 对象
        
        Returns:
            True 如果职位应该被保留
        """
        title = job.title.lower()
        
        # 首先检查是否应该排除
        if self._matches_any_pattern(title, self._exclude_patterns):
            logger.debug(f"Excluded (matched exclude keyword): {job.title}")
            return False
        
        # 然后检查是否应该包含
        if self._matches_any_pattern(title, self._include_patterns):
            logger.debug(f"Included (matched include keyword): {job.title}")
            return True
        
        # 默认不包含
        logger.debug(f"Excluded (no match): {job.title}")
        return False
    
    def _matches_any_pattern(
        self,
        text: str,
        patterns: list[re.Pattern]
    ) -> bool:
        """检查文本是否匹配任一模式"""
        for pattern in patterns:
            if pattern.search(text):
                return True
        return False
    
    def filter_jobs(self, jobs: list[Job]) -> list[Job]:
        """
        过滤职位列表
        
        Args:
            jobs: 原始职位列表
        
        Returns:
            过滤后的职位列表
        """
        filtered = [job for job in jobs if self.should_include(job)]
        
        logger.info(
            f"Filtered jobs: {len(filtered)}/{len(jobs)} "
            f"({len(jobs) - len(filtered)} excluded)"
        )
        
        return filtered


# 默认过滤器实例
default_filter = JobFilter()


def filter_jobs(jobs: list[Job]) -> list[Job]:
    """使用默认过滤器过滤职位"""
    return default_filter.filter_jobs(jobs)
