"""
配置文件 - Crypto Job Monitor
"""
import os
from pathlib import Path

# ============== 项目路径 ==============
BASE_DIR = Path(__file__).parent
STORAGE_DIR = BASE_DIR / "storage"
STORAGE_FILE = STORAGE_DIR / "jobs.json"

# ============== Telegram 配置 ==============
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ============== VC Portfolio Job Boards ==============
# 支持 Getro 和 Consider 两种平台
# platform: "getro" 或 "consider"

GETRO_BOARDS = {
    # ===== Consider 平台 =====
    "paradigm": {
        "name": "Paradigm Portfolio",
        "base_url": "https://jobs.paradigm.xyz",
        "platform": "consider",
        "enabled": True,
    },
    
    # ===== Getro 平台 =====
    "multicoin": {
        "name": "Multicoin Capital Portfolio",
        "base_url": "https://jobs.multicoin.capital",
        "platform": "getro",
        "enabled": True,
    },
    "polychain": {
        "name": "Polychain Capital Portfolio",
        "base_url": "https://jobs.polychain.capital",
        "platform": "getro",
        "enabled": True,
    },
    "dragonfly": {
        "name": "Dragonfly Portfolio",
        "base_url": "https://jobs.dragonfly.xyz",
        "platform": "getro",
        "enabled": True,
    },
    "electric": {
        "name": "Electric Capital Portfolio",
        "base_url": "https://jobs.electriccapital.com",
        "platform": "getro",
        "enabled": True,
    },
    "blockchain_capital": {
        "name": "Blockchain Capital Portfolio",
        "base_url": "https://jobs.blockchaincapital.com",
        "platform": "getro",
        "enabled": True,
    },
    "pantera": {
        "name": "Pantera Capital Portfolio",
        "base_url": "https://jobs.panteracapital.com",
        "platform": "getro",
        "enabled": True,
    },
    "galaxy": {
        "name": "Galaxy Ventures Portfolio",
        "base_url": "https://venturecareers.galaxy.com",
        "platform": "getro",
        "enabled": True,
    },
    "framework": {
        "name": "Framework Ventures Portfolio",
        "base_url": "https://jobs.framework.ventures",
        "platform": "getro",
        "enabled": True,
    },
    "variant": {
        "name": "Variant Fund Portfolio",
        "base_url": "https://jobs.variant.fund",
        "platform": "getro",
        "enabled": True,
    },
    "1kx": {
        "name": "1kx Portfolio",
        "base_url": "https://jobs.1kx.network",
        "platform": "getro",
        "enabled": True,
    },
}

# ============== 其他数据源 ==============
OTHER_SOURCES = {
    "web3career": {
        "name": "Web3.career",
        "url": "https://web3.career/non-tech-jobs",
        "enabled": True,
    },
}

# ============== 职位过滤配置 ==============
# 目标职位类型（标题必须包含至少一个关键词）
# 投资、研究、战略、运营、BD、增长等核心岗位
INCLUDE_KEYWORDS = [
    # 投资相关
    "investment", "investor", "venture", "vc", "portfolio",
    "principal", "associate",  # VC 常见职级
    
    # 研究相关
    "research", "researcher", "analyst",
    
    # 战略相关
    "strategy", "strategic", "strategist",
    
    # 运营相关
    "operations", "ops", "operating",
    "chief of staff", "cos",
    
    # BD / 合作伙伴
    "business development", " bd ", "partnerships", "partner",
    "ecosystem", "alliances",
    
    # 增长 / 市场（偏战略）
    "growth", "marketing", "gtm", "go-to-market",
    
    # 产品（非技术）
    "product manager", "product lead", "head of product",
    
    # 社区 / 生态
    "community", "ambassador", "evangelist",
    
    # 高管
    "director", "head of", "vp ", "vice president",
    "general manager", "gm",
]

# 排除的职位类型（标题包含这些词会被过滤掉）
EXCLUDE_KEYWORDS = [
    # === 工程/开发类（全部排除）===
    "engineer", "engineering", "developer", "development",
    "frontend", "front-end", "front end",
    "backend", "back-end", "back end",
    "fullstack", "full-stack", "full stack",
    "smart contract", "solidity", "rust", "golang", "python",
    "devops", "sre", "site reliability", "infrastructure",
    "security engineer", "security researcher",
    "qa", "quality assurance", "test engineer", "sdet",
    "data engineer", "ml engineer", "machine learning",
    "blockchain developer", "protocol engineer", "core dev",
    "software", "architect", "technical lead", "tech lead",
    "cto", "vp engineering", "head of engineering",
    
    # === 财务类（排除）===
    "finance", "financial", "accounting", "accountant",
    "treasury", "controller", "cfo", "bookkeeper",
    "tax", "audit", "auditor",
    
    # === 法务类（排除）===
    "legal", "lawyer", "attorney", "counsel",
    "compliance", "regulatory", "aml", "kyc",
    
    # === HR类（排除）===
    "human resources", " hr ", "people ops", "people operations",
    "talent", "recruiting", "recruiter", "recruitment",
    
    # === 销售类（排除）===
    "sales", "account executive", " ae ", "account manager",
    "business representative", "sales development", "sdr",
    
    # === 其他专业类（排除）===
    "customer support", "customer success", "support engineer",
    "designer", "design", "ui/ux", "ux", "graphic",
]

# ============== 请求配置 ==============
REQUEST_TIMEOUT = 30  # 秒
REQUEST_DELAY = 1.5  # 请求间隔（秒），避免被封
MAX_RETRIES = 3  # 最大重试次数

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

# ============== Telegram 消息配置 ==============
# 每批发送的最大消息数（避免触发 Telegram 限制）
MAX_MESSAGES_PER_BATCH = 20

# 消息发送间隔（秒）
MESSAGE_DELAY = 0.5

# ============== 日志配置 ==============
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
