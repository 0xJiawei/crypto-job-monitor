"""
web3.career 爬虫

web3.career 是最大的 Web3 招聘聚合平台之一，
提供非技术类职位的专门分类页面。
"""
import requests
import time
import re
from typing import Optional
from bs4 import BeautifulSoup

from .base import BaseScraper, Job
import config


class Web3CareerScraper(BaseScraper):
    """web3.career 爬虫"""
    
    def __init__(self):
        super().__init__(
            name="web3career",
            source_name="Web3.career"
        )
        self.base_url = "https://web3.career"
        # 非技术类职位页面
        self.categories = [
            "/non-tech-jobs",
            "/analyst-jobs",
            "/community-manager-jobs",
        ]
    
    def fetch_jobs(self) -> list[Job]:
        """获取所有职位"""
        all_jobs = []
        seen_urls = set()
        
        for category in self.categories:
            jobs = self._fetch_category(category)
            for job in jobs:
                if job.url not in seen_urls:
                    all_jobs.append(job)
                    seen_urls.add(job.url)
            time.sleep(config.REQUEST_DELAY)
        
        return all_jobs
    
    def _fetch_category(self, category_path: str) -> list[Job]:
        """获取某个分类的职位"""
        jobs = []
        page = 1
        max_pages = 10  # 每个分类最多爬取10页
        
        while page <= max_pages:
            url = f"{self.base_url}{category_path}"
            if page > 1:
                url += f"?page={page}"
            
            page_jobs = self._fetch_page(url)
            
            if not page_jobs:
                break
            
            jobs.extend(page_jobs)
            
            # 如果职位数量少于预期，可能是最后一页
            if len(page_jobs) < 15:
                break
            
            page += 1
            time.sleep(config.REQUEST_DELAY)
        
        return jobs
    
    def _fetch_page(self, url: str) -> list[Job]:
        """获取单页数据"""
        jobs = []
        
        for attempt in range(config.MAX_RETRIES):
            try:
                response = requests.get(
                    url,
                    headers=config.HEADERS,
                    timeout=config.REQUEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "lxml")
                    job_cards = soup.select("tr.table_row, div.job-card, a.job-link")
                    
                    # 尝试不同的选择器
                    if not job_cards:
                        job_cards = soup.select("[data-job-id], .job-item")
                    
                    for card in job_cards:
                        job = self._parse_job_card(card)
                        if job:
                            jobs.append(job)
                    
                    return jobs
                
                elif response.status_code == 404:
                    self.logger.warning(f"Page not found: {url}")
                    return []
                
            except requests.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                time.sleep(2 ** attempt)
        
        return []
    
    def _parse_job_card(self, card) -> Optional[Job]:
        """解析职位卡片"""
        try:
            # 获取标题和链接
            title_elem = (
                card.select_one("h2, h3, .job-title, td:first-child a") or
                card.select_one("a[href*='/']")
            )
            
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            if not title:
                return None
            
            # 获取 URL
            if card.name == "a":
                href = card.get("href", "")
            else:
                link_elem = card.select_one("a[href]")
                href = link_elem.get("href", "") if link_elem else ""
            
            if not href:
                return None
            
            # 构建完整 URL
            if href.startswith("/"):
                url = f"{self.base_url}{href}"
            elif href.startswith("http"):
                url = href
            else:
                url = f"{self.base_url}/{href}"
            
            # 获取公司名称
            company_elem = card.select_one(".company, .company-name, td:nth-child(2)")
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"
            
            # 获取地点
            location_elem = card.select_one(".location, .job-location, td:nth-child(3)")
            location = location_elem.get_text(strip=True) if location_elem else ""
            
            # 获取薪资
            salary_elem = card.select_one(".salary, .job-salary, td:nth-child(4)")
            salary = salary_elem.get_text(strip=True) if salary_elem else ""
            
            # 判断是否远程
            remote = "remote" in location.lower() if location else False
            
            return Job(
                title=title,
                company=company,
                url=url,
                source=self.source_name,
                location=location,
                salary=salary,
                remote=remote,
            )
        
        except Exception as e:
            self.logger.warning(f"Failed to parse job card: {e}")
            return None


# 创建 web3.career 爬虫实例的工厂函数
def create_web3career_scraper() -> Web3CareerScraper:
    """创建 web3.career 爬虫"""
    return Web3CareerScraper()
