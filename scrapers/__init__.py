"""
爬虫模块
"""
from .base import BaseScraper, Job
from .getro import GetroScraper, create_getro_scrapers
from .web3career import Web3CareerScraper, create_web3career_scraper

__all__ = [
    "BaseScraper",
    "Job",
    "GetroScraper",
    "create_getro_scrapers",
    "Web3CareerScraper",
    "create_web3career_scraper",
]
