"""
加密 VC 投资组合公司 Job Board 爬虫

使用公共 API 获取职位：
- Greenhouse API: 大多数加密公司使用
- Ashby API: 新兴 ATS，Paradigm 等使用
- Lever API: 部分公司使用
"""
import requests
import time
import re
from typing import Optional
from bs4 import BeautifulSoup

from .base import BaseScraper, Job
import config


class GreenhouseScraper(BaseScraper):
    """
    Greenhouse Job Board API 爬虫
    
    公共 API 文档: https://developers.greenhouse.io/job-board.html
    API 格式: https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs
    """
    
    def __init__(self, company_name: str, board_token: str, source_name: str = None):
        super().__init__(
            name=f"greenhouse_{board_token}",
            source_name=source_name or company_name
        )
        self.company_name = company_name
        self.board_token = board_token
        self.api_url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
    
    def fetch_jobs(self) -> list[Job]:
        """获取职位列表"""
        jobs = []
        
        try:
            # Greenhouse API 支持 content=true 参数获取完整职位描述
            response = requests.get(
                self.api_url,
                params={"content": "true"},
                headers={"Accept": "application/json"},
                timeout=config.REQUEST_TIMEOUT
            )
            
            if response.status_code != 200:
                self.logger.warning(f"[{self.board_token}] HTTP {response.status_code}")
                return []
            
            data = response.json()
            job_list = data.get("jobs", [])
            
            for job_data in job_list:
                title = job_data.get("title", "")
                job_id = job_data.get("id")
                absolute_url = job_data.get("absolute_url", "")
                
                if not title or not absolute_url:
                    continue
                
                # 提取地点
                location_data = job_data.get("location", {})
                location = location_data.get("name", "") if isinstance(location_data, dict) else ""
                
                # 提取部门
                departments = job_data.get("departments", [])
                department = departments[0].get("name", "") if departments else ""
                
                # 检查是否远程
                remote = "remote" in location.lower() if location else False
                
                jobs.append(Job(
                    title=title,
                    company=self.company_name,
                    url=absolute_url,
                    source=self.source_name,
                    location=location,
                    remote=remote,
                    description=department,  # 用部门作为额外信息
                ))
            
            self.logger.info(f"[{self.board_token}] Found {len(jobs)} jobs via Greenhouse API")
            
        except Exception as e:
            self.logger.error(f"[{self.board_token}] Greenhouse API error: {e}")
        
        return jobs


class AshbyScraper(BaseScraper):
    """
    Ashby Job Board API 爬虫
    
    API 格式: https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobBoardWithTeams
    """
    
    def __init__(self, company_name: str, board_slug: str, source_name: str = None):
        super().__init__(
            name=f"ashby_{board_slug}",
            source_name=source_name or company_name
        )
        self.company_name = company_name
        self.board_slug = board_slug
        self.api_url = "https://jobs.ashbyhq.com/api/non-user-graphql"
    
    def fetch_jobs(self) -> list[Job]:
        """获取职位列表"""
        jobs = []
        
        try:
            # Ashby 使用 GraphQL API
            query = {
                "operationName": "ApiJobBoardWithTeams",
                "variables": {
                    "organizationHostedJobsPageName": self.board_slug
                },
                "query": """
                query ApiJobBoardWithTeams($organizationHostedJobsPageName: String!) {
                    jobBoard: jobBoardWithTeams(
                        organizationHostedJobsPageName: $organizationHostedJobsPageName
                    ) {
                        teams {
                            name
                            jobs {
                                id
                                title
                                locationName
                                employmentType
                                isRemote
                            }
                        }
                    }
                }
                """
            }
            
            response = requests.post(
                self.api_url,
                json=query,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                timeout=config.REQUEST_TIMEOUT
            )
            
            if response.status_code != 200:
                self.logger.warning(f"[{self.board_slug}] HTTP {response.status_code}")
                return []
            
            data = response.json()
            job_board = data.get("data", {}).get("jobBoard", {})
            teams = job_board.get("teams", []) if job_board else []
            
            for team in teams:
                team_name = team.get("name", "")
                team_jobs = team.get("jobs", [])
                
                for job_data in team_jobs:
                    title = job_data.get("title", "")
                    job_id = job_data.get("id", "")
                    location = job_data.get("locationName", "")
                    employment_type = job_data.get("employmentType", "")
                    is_remote = job_data.get("isRemote", False)
                    
                    if not title or not job_id:
                        continue
                    
                    # 构建职位 URL
                    job_url = f"https://jobs.ashbyhq.com/{self.board_slug}/{job_id}"
                    
                    jobs.append(Job(
                        title=title,
                        company=self.company_name,
                        url=job_url,
                        source=self.source_name,
                        location=location,
                        remote=is_remote,
                        job_type=employment_type,
                        description=team_name,  # 用团队名作为额外信息
                    ))
            
            self.logger.info(f"[{self.board_slug}] Found {len(jobs)} jobs via Ashby API")
            
        except Exception as e:
            self.logger.error(f"[{self.board_slug}] Ashby API error: {e}")
        
        return jobs


class LeverScraper(BaseScraper):
    """
    Lever Job Board API 爬虫
    
    API 格式: https://api.lever.co/v0/postings/{company}
    """
    
    def __init__(self, company_name: str, lever_slug: str, source_name: str = None):
        super().__init__(
            name=f"lever_{lever_slug}",
            source_name=source_name or company_name
        )
        self.company_name = company_name
        self.lever_slug = lever_slug
        self.api_url = f"https://api.lever.co/v0/postings/{lever_slug}"
    
    def fetch_jobs(self) -> list[Job]:
        """获取职位列表"""
        jobs = []
        
        try:
            response = requests.get(
                self.api_url,
                headers={"Accept": "application/json"},
                timeout=config.REQUEST_TIMEOUT
            )
            
            if response.status_code != 200:
                self.logger.warning(f"[{self.lever_slug}] HTTP {response.status_code}")
                return []
            
            job_list = response.json()
            
            for job_data in job_list:
                title = job_data.get("text", "")
                job_url = job_data.get("hostedUrl", "")
                
                if not title or not job_url:
                    continue
                
                # 提取分类信息
                categories = job_data.get("categories", {})
                location = categories.get("location", "")
                team = categories.get("team", "")
                commitment = categories.get("commitment", "")  # Full-time, Part-time 等
                
                # 检查是否远程
                workplace_type = job_data.get("workplaceType", "")
                remote = workplace_type == "remote" or "remote" in location.lower()
                
                jobs.append(Job(
                    title=title,
                    company=self.company_name,
                    url=job_url,
                    source=self.source_name,
                    location=location,
                    remote=remote,
                    job_type=commitment,
                    description=team,
                ))
            
            self.logger.info(f"[{self.lever_slug}] Found {len(jobs)} jobs via Lever API")
            
        except Exception as e:
            self.logger.error(f"[{self.lever_slug}] Lever API error: {e}")
        
        return jobs


class WorkableScraper(BaseScraper):
    """
    Workable Job Board 爬虫
    
    API 格式: https://apply.workable.com/api/v1/widget/accounts/{subdomain}
    """
    
    def __init__(self, company_name: str, subdomain: str, source_name: str = None):
        super().__init__(
            name=f"workable_{subdomain}",
            source_name=source_name or company_name
        )
        self.company_name = company_name
        self.subdomain = subdomain
        self.api_url = f"https://apply.workable.com/api/v1/widget/accounts/{subdomain}"
    
    def fetch_jobs(self) -> list[Job]:
        """获取职位列表"""
        jobs = []
        
        try:
            response = requests.get(
                self.api_url,
                headers={"Accept": "application/json"},
                timeout=config.REQUEST_TIMEOUT
            )
            
            if response.status_code != 200:
                self.logger.warning(f"[{self.subdomain}] HTTP {response.status_code}")
                return []
            
            data = response.json()
            job_list = data.get("jobs", [])
            
            for job_data in job_list:
                title = job_data.get("title", "")
                shortcode = job_data.get("shortcode", "")
                
                if not title or not shortcode:
                    continue
                
                # 构建职位 URL
                job_url = f"https://apply.workable.com/{self.subdomain}/j/{shortcode}/"
                
                # 提取地点
                location_data = job_data.get("location", {})
                city = location_data.get("city", "")
                country = location_data.get("country", "")
                location = f"{city}, {country}".strip(", ")
                
                # 检查远程
                remote = job_data.get("remote", False)
                
                jobs.append(Job(
                    title=title,
                    company=self.company_name,
                    url=job_url,
                    source=self.source_name,
                    location=location,
                    remote=remote,
                ))
            
            self.logger.info(f"[{self.subdomain}] Found {len(jobs)} jobs via Workable API")
            
        except Exception as e:
            self.logger.error(f"[{self.subdomain}] Workable API error: {e}")
        
        return jobs


def create_vc_portfolio_scrapers() -> list[BaseScraper]:
    """
    创建 VC 投资组合公司的爬虫
    
    这些是 Top Crypto VC 投资的公司，使用各种 ATS 平台
    """
    scrapers = []
    
    # ============ Greenhouse 公司 ============
    greenhouse_companies = [
        # Paradigm 投资组合
        ("Uniswap", "uniswaplabs", "Paradigm Portfolio"),
        ("Optimism", "optimismpbc", "Paradigm Portfolio"),
        ("Blur", "blur71", "Paradigm Portfolio"),
        ("Phantom", "phantom72", "Paradigm Portfolio"),
        ("OpenSea", "opensea", "Paradigm Portfolio"),
        ("dYdX", "dydx", "Paradigm Portfolio"),
        ("Fireblocks", "fireblocks", "Paradigm Portfolio"),
        ("Chainalysis", "chainalysis", "Paradigm Portfolio"),
        
        # Multicoin 投资组合
        ("Helium", "heliumfoundation", "Multicoin Portfolio"),
        ("Solana Foundation", "solanafoundation", "Multicoin Portfolio"),
        
        # Dragonfly 投资组合
        ("Matter Labs", "matterlabs", "Dragonfly Portfolio"),
        ("Axelar", "axelarnetwork", "Dragonfly Portfolio"),
        
        # Polychain 投资组合
        ("Celestia", "celestiaorg", "Polychain Portfolio"),
        
        # a16z crypto 投资组合
        ("Coinbase", "coinbase", "a16z Portfolio"),
        ("Alchemy", "alchemy", "a16z Portfolio"),
        ("LayerZero Labs", "layerzerolabs", "a16z Portfolio"),
        
        # 其他顶级加密公司
        ("Bitwise", "bitwiseinvestments", "Top Crypto"),
        ("Figment", "figment", "Top Crypto"),
        ("Gauntlet", "gauntlet14", "Top Crypto"),
        ("Jump Crypto", "jumpcrypto", "Top Crypto"),
        ("Wintermute", "wintermute", "Top Crypto"),
        ("Messari", "messari", "Top Crypto"),
        ("Delphi Digital", "delphidigital", "Top Crypto"),
        ("The Block", "theblock", "Top Crypto"),
        ("Paxos", "paxos", "Top Crypto"),
        ("Circle", "circle", "Top Crypto"),
        ("Ledger", "ledger", "Top Crypto"),
        ("ConsenSys", "consensys", "Top Crypto"),
        ("Polygon Labs", "polygonlabs", "Top Crypto"),
        ("Aave", "aavecompany", "Top Crypto"),
        ("Compound Labs", "compoundfinance", "Top Crypto"),
        ("Chainlink Labs", "chainlinklabs", "Top Crypto"),
        ("Kraken", "kraboratory", "Top Crypto"),
        ("Binance", "binance", "Top Crypto"),
        ("OKX", "oloey", "Top Crypto"),
        ("Bybit", "bybit", "Top Crypto"),
        ("Gemini", "gemini", "Top Crypto"),
        ("Ripple", "ripple", "Top Crypto"),
        ("BlockFi", "blockfi", "Top Crypto"),
        ("Anchorage", "anchorage", "Top Crypto"),
        ("Galaxy Digital", "galaxydigital", "Top Crypto"),
        ("DCG", "digitalcurrencygroup", "Top Crypto"),
        ("Grayscale", "grayscaleinvest", "Top Crypto"),
    ]
    
    for company_name, board_token, source_name in greenhouse_companies:
        scrapers.append(GreenhouseScraper(company_name, board_token, source_name))
    
    # ============ Ashby 公司 ============
    ashby_companies = [
        ("Paradigm", "paradigm", "Paradigm"),
        ("Eigenlayer", "eigenlabs", "Top Crypto"),
        ("Monad", "monad", "Dragonfly Portfolio"),
        ("Movement Labs", "movementlabs", "Polychain Portfolio"),
        ("Eclipse", "eclipse", "Polychain Portfolio"),
        ("Syndicate", "syndicate", "a16z Portfolio"),
        ("Privy", "privy", "Paradigm Portfolio"),
        ("Berachain", "berachain", "Polychain Portfolio"),
        ("Hyperlane", "hyperlane", "Top Crypto"),
        ("Superscrypt", "superscrypt", "Top Crypto"),
    ]
    
    for company_name, board_slug, source_name in ashby_companies:
        scrapers.append(AshbyScraper(company_name, board_slug, source_name))
    
    # ============ Lever 公司 ============
    lever_companies = [
        ("Solana Labs", "solana", "Multicoin Portfolio"),
        ("Aptos Labs", "aptoslabs", "a16z Portfolio"),
        ("Sui (Mysten Labs)", "mystenlabs", "a16z Portfolio"),
        ("Worldcoin", "worldcoinorg", "a16z Portfolio"),
        ("Nansen", "nansen", "Top Crypto"),
        ("Ondo Finance", "ondofinance", "Pantera Portfolio"),
        ("Arbitrum (Offchain Labs)", "offchainlabs", "Top Crypto"),
        ("StarkWare", "starkware", "Paradigm Portfolio"),
        ("Sei Labs", "sei-labs", "Multicoin Portfolio"),
        ("Scroll", "scroll", "Polychain Portfolio"),
        ("Linea (Consensys)", "linea-d0", "Top Crypto"),
    ]
    
    for company_name, lever_slug, source_name in lever_companies:
        scrapers.append(LeverScraper(company_name, lever_slug, source_name))
    
    # ============ Workable 公司 ============
    workable_companies = [
        ("Safe", "safe-global", "Top Crypto"),
        ("Gnosis", "gnosis", "Top Crypto"),
    ]
    
    for company_name, subdomain, source_name in workable_companies:
        scrapers.append(WorkableScraper(company_name, subdomain, source_name))
    
    return scrapers


# 保持向后兼容
def create_getro_scrapers() -> list[BaseScraper]:
    """向后兼容函数"""
    return create_vc_portfolio_scrapers()
