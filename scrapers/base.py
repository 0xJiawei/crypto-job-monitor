"""
爬虫基类和 Job 数据模型
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
import hashlib
import logging

logger = logging.getLogger(__name__)


@dataclass
class Job:
    """职位数据模型"""
    
    # 必填字段
    title: str
    company: str
    url: str
    source: str  # 数据来源（如 "Paradigm Portfolio"）
    
    # 可选字段
    location: str = ""
    salary: str = ""
    job_type: str = ""  # Full-time, Part-time, Contract 等
    remote: bool = False
    description: str = ""
    posted_date: str = ""
    
    # 元数据
    scraped_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    @property
    def unique_id(self) -> str:
        """生成唯一标识符，用于去重"""
        # 使用 title + company + url 生成唯一ID
        key = f"{self.title.lower()}|{self.company.lower()}|{self.url}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def to_dict(self) -> dict:
        """转换为字典"""
        data = asdict(self)
        data["unique_id"] = self.unique_id
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> "Job":
        """从字典创建 Job 对象"""
        # 移除 unique_id，因为它是计算属性
        data = {k: v for k, v in data.items() if k != "unique_id"}
        return cls(**data)
    
    def format_telegram_message(self) -> str:
        """格式化为 Telegram 消息"""
        lines = [
            f"📌 <b>{self._escape_html(self.title)}</b>",
            f"🏢 {self._escape_html(self.company)}",
            f"📂 <i>via {self._escape_html(self.source)}</i>",
        ]
        
        if self.location:
            location_text = self.location
            if self.remote:
                location_text += " (Remote OK)"
            lines.append(f"📍 {self._escape_html(location_text)}")
        elif self.remote:
            lines.append("📍 Remote")
        
        if self.salary:
            lines.append(f"💰 {self._escape_html(self.salary)}")
        
        if self.job_type:
            lines.append(f"⏰ {self._escape_html(self.job_type)}")
        
        lines.extend([
            "",
            f"🔗 <a href=\"{self.url}\">Apply Now</a>",
        ])
        
        # 添加标签
        tags = self._generate_tags()
        if tags:
            lines.extend(["", tags])
        
        return "\n".join(lines)
    
    def _escape_html(self, text: str) -> str:
        """转义 HTML 特殊字符"""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
    
    def _generate_tags(self) -> str:
        """生成标签"""
        tags = ["#crypto", "#web3"]
        
        title_lower = self.title.lower()
        
        if any(kw in title_lower for kw in ["research", "analyst"]):
            tags.append("#research")
        if any(kw in title_lower for kw in ["invest", "vc", "venture", "principal"]):
            tags.append("#investment")
        if any(kw in title_lower for kw in ["strateg"]):
            tags.append("#strategy")
        if any(kw in title_lower for kw in ["operation", "ops"]):
            tags.append("#operations")
        if any(kw in title_lower for kw in ["business development", " bd ", "partner"]):
            tags.append("#bizdev")
        if any(kw in title_lower for kw in ["growth", "marketing"]):
            tags.append("#growth")
        if any(kw in title_lower for kw in ["product"]):
            tags.append("#product")
        if any(kw in title_lower for kw in ["community"]):
            tags.append("#community")
        
        return " ".join(tags[:5])  # 最多5个标签


class BaseScraper(ABC):
    """爬虫基类"""
    
    def __init__(self, name: str, source_name: str):
        """
        初始化爬虫
        
        Args:
            name: 爬虫名称（用于日志）
            source_name: 数据源名称（显示在消息中）
        """
        self.name = name
        self.source_name = source_name
        self.logger = logging.getLogger(f"scraper.{name}")
    
    @abstractmethod
    def fetch_jobs(self) -> list[Job]:
        """
        获取职位列表
        
        Returns:
            Job 对象列表
        """
        pass
    
    def scrape(self) -> list[Job]:
        """
        执行爬取（带错误处理）
        
        Returns:
            Job 对象列表
        """
        try:
            self.logger.info(f"Starting scrape: {self.name}")
            jobs = self.fetch_jobs()
            self.logger.info(f"Scraped {len(jobs)} jobs from {self.name}")
            return jobs
        except Exception as e:
            self.logger.error(f"Error scraping {self.name}: {e}")
            return []
