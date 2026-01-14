"""
存储管理器

负责保存和读取已知职位数据，用于检测新职位。
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from scrapers.base import Job
import config

logger = logging.getLogger(__name__)


class StorageManager:
    """存储管理器"""
    
    def __init__(self, storage_file: Optional[Path] = None):
        """
        初始化存储管理器
        
        Args:
            storage_file: 存储文件路径（默认使用配置）
        """
        self.storage_file = storage_file or config.STORAGE_FILE
        self._ensure_storage_dir()
        self._known_jobs: dict[str, dict] = {}
        self._load()
    
    def _ensure_storage_dir(self):
        """确保存储目录存在"""
        storage_dir = self.storage_file.parent
        storage_dir.mkdir(parents=True, exist_ok=True)
    
    def _load(self):
        """从文件加载已知职位"""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._known_jobs = data.get("jobs", {})
                    logger.info(f"Loaded {len(self._known_jobs)} known jobs")
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load storage: {e}")
                self._known_jobs = {}
        else:
            logger.info("No existing storage file, starting fresh")
            self._known_jobs = {}
    
    def _save(self):
        """保存到文件"""
        try:
            data = {
                "jobs": self._known_jobs,
                "updated_at": datetime.utcnow().isoformat(),
                "total_count": len(self._known_jobs),
            }
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self._known_jobs)} jobs to storage")
        except IOError as e:
            logger.error(f"Failed to save storage: {e}")
    
    def is_known(self, job: Job) -> bool:
        """
        检查职位是否已知
        
        Args:
            job: Job 对象
        
        Returns:
            True 如果职位已存在
        """
        return job.unique_id in self._known_jobs
    
    def add_job(self, job: Job):
        """
        添加职位到存储
        
        Args:
            job: Job 对象
        """
        self._known_jobs[job.unique_id] = {
            "title": job.title,
            "company": job.company,
            "url": job.url,
            "source": job.source,
            "added_at": datetime.utcnow().isoformat(),
        }
    
    def add_jobs(self, jobs: list[Job]):
        """
        批量添加职位
        
        Args:
            jobs: Job 对象列表
        """
        for job in jobs:
            self.add_job(job)
    
    def find_new_jobs(self, jobs: list[Job]) -> list[Job]:
        """
        从职位列表中找出新职位
        
        Args:
            jobs: 所有职位列表
        
        Returns:
            新职位列表
        """
        new_jobs = []
        for job in jobs:
            if not self.is_known(job):
                new_jobs.append(job)
        
        logger.info(f"Found {len(new_jobs)} new jobs out of {len(jobs)}")
        return new_jobs
    
    def mark_as_seen(self, jobs: list[Job]):
        """
        标记职位为已见（保存到存储）
        
        Args:
            jobs: Job 对象列表
        """
        self.add_jobs(jobs)
        self._save()
    
    def get_stats(self) -> dict:
        """获取存储统计信息"""
        return {
            "total_jobs": len(self._known_jobs),
            "storage_file": str(self.storage_file),
        }
    
    def is_first_run(self) -> bool:
        """
        检查是否首次运行
        
        Returns:
            True 如果存储为空（首次运行）
        """
        return len(self._known_jobs) == 0
    
    def cleanup_old_jobs(self, days: int = 90):
        """
        清理超过指定天数的旧职位记录
        
        Args:
            days: 保留的天数
        """
        from datetime import timedelta
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        old_count = len(self._known_jobs)
        
        self._known_jobs = {
            job_id: job_data
            for job_id, job_data in self._known_jobs.items()
            if datetime.fromisoformat(job_data.get("added_at", "2020-01-01")) > cutoff
        }
        
        removed = old_count - len(self._known_jobs)
        if removed > 0:
            logger.info(f"Cleaned up {removed} old jobs")
            self._save()
