"""
爬虫模块
"""
from .base import BaseScraper, Job
from .getro import (
    GreenhouseScraper,
    AshbyScraper,
    LeverScraper,
    WorkableScraper,
    create_getro_scrapers,
    create_vc_portfolio_scrapers,
)
from .web3career import Web3CareerScraper, create_web3career_scraper


def create_all_scrapers() -> list[BaseScraper]:
    """创建所有爬虫"""
    scrapers = []
    scrapers.extend(create_vc_portfolio_scrapers())
    scrapers.append(create_web3career_scraper())
    return scrapers


__all__ = [
    "BaseScraper",
    "Job",
    "GreenhouseScraper",
    "AshbyScraper",
    "LeverScraper",
    "WorkableScraper",
    "Web3CareerScraper",
    "create_getro_scrapers",
    "create_vc_portfolio_scrapers",
    "create_web3career_scraper",
    "create_all_scrapers",
]
