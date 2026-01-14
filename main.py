#!/usr/bin/env python3
"""
Crypto Job Monitor - 主程序入口

监控 Crypto VC Portfolio Job Boards，
检测新职位并推送到 Telegram。
"""
import sys
import logging
import asyncio
from datetime import datetime

import config
from scrapers import create_getro_scrapers, create_web3career_scraper, Job
from filters import filter_jobs
from storage import StorageManager
from notifier import TelegramNotifier
from dashboard import generate_dashboard


def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def collect_all_jobs() -> tuple[list[Job], list[str]]:
    """
    从所有数据源收集职位
    
    Returns:
        (职位列表, 数据源名称列表)
    """
    all_jobs = []
    sources = []
    
    # 创建所有 Getro 爬虫
    getro_scrapers = create_getro_scrapers()
    
    for scraper in getro_scrapers:
        jobs = scraper.scrape()
        if jobs:
            all_jobs.extend(jobs)
            sources.append(scraper.source_name)
    
    # 创建 web3.career 爬虫
    try:
        web3career_scraper = create_web3career_scraper()
        jobs = web3career_scraper.scrape()
        if jobs:
            all_jobs.extend(jobs)
            sources.append(web3career_scraper.source_name)
    except Exception as e:
        logging.warning(f"Failed to scrape web3.career: {e}")
    
    return all_jobs, sources


def deduplicate_jobs(jobs: list[Job]) -> list[Job]:
    """
    去重职位列表
    
    Args:
        jobs: 原始职位列表
    
    Returns:
        去重后的职位列表
    """
    seen = set()
    unique_jobs = []
    
    for job in jobs:
        if job.unique_id not in seen:
            seen.add(job.unique_id)
            unique_jobs.append(job)
    
    logging.info(f"Deduplicated: {len(unique_jobs)}/{len(jobs)} unique jobs")
    return unique_jobs


async def main():
    """主函数"""
    setup_logging()
    logger = logging.getLogger("main")
    
    logger.info("=" * 50)
    logger.info("Crypto Job Monitor Started")
    logger.info(f"Time: {datetime.utcnow().isoformat()}")
    logger.info("=" * 50)
    
    # 1. 收集所有职位
    logger.info("Step 1: Collecting jobs from all sources...")
    all_jobs, sources = collect_all_jobs()
    logger.info(f"Collected {len(all_jobs)} jobs from {len(sources)} sources")
    
    if not all_jobs:
        logger.warning("No jobs collected, exiting")
        return
    
    # 2. 去重
    logger.info("Step 2: Deduplicating jobs...")
    unique_jobs = deduplicate_jobs(all_jobs)
    
    # 3. 过滤（只保留目标类型的职位）
    logger.info("Step 3: Filtering jobs...")
    filtered_jobs = filter_jobs(unique_jobs)
    logger.info(f"After filtering: {len(filtered_jobs)} jobs")
    
    if not filtered_jobs:
        logger.info("No matching jobs after filtering")
        return
    
    # 4. 检测新职位
    logger.info("Step 4: Detecting new jobs...")
    storage = StorageManager()
    
    # 检查是否首次运行
    is_first_run = storage.is_first_run()
    
    new_jobs = storage.find_new_jobs(filtered_jobs)
    logger.info(f"Found {len(new_jobs)} new jobs")
    
    # 5. 发送通知
    if new_jobs:
        if is_first_run:
            logger.info(
                "First run detected. Recording all jobs but not sending notifications."
            )
            # 首次运行只记录，不发送通知（避免消息轰炸）
            storage.mark_as_seen(new_jobs)
            logger.info(f"Recorded {len(new_jobs)} jobs for future comparison")
        else:
            logger.info("Step 5: Sending notifications...")
            
            try:
                notifier = TelegramNotifier()
                success, fail = await notifier.send_job_notifications(new_jobs)
                logger.info(f"Sent {success} notifications, {fail} failed")
                
                # 只有发送成功的才标记为已见
                if success > 0:
                    storage.mark_as_seen(new_jobs)
                    
            except ValueError as e:
                logger.error(f"Telegram configuration error: {e}")
                logger.info("Saving jobs anyway for next run")
                storage.mark_as_seen(new_jobs)
    else:
        logger.info("No new jobs to notify")
    
    # 6. 生成 Dashboard
    logger.info("Step 6: Generating dashboard...")
    try:
        dashboard_path = generate_dashboard(filtered_jobs, "dashboard.html")
        logger.info(f"Dashboard generated: {dashboard_path}")
    except Exception as e:
        logger.error(f"Failed to generate dashboard: {e}")
    
    # 7. 清理旧记录（可选）
    storage.cleanup_old_jobs(days=90)
    
    # 8. 打印统计
    stats = storage.get_stats()
    logger.info("=" * 50)
    logger.info("Summary:")
    logger.info(f"  - Sources scraped: {len(sources)}")
    logger.info(f"  - Total jobs collected: {len(all_jobs)}")
    logger.info(f"  - After filtering: {len(filtered_jobs)}")
    logger.info(f"  - New jobs found: {len(new_jobs)}")
    logger.info(f"  - Total jobs in storage: {stats['total_jobs']}")
    logger.info("=" * 50)
    logger.info("Crypto Job Monitor Completed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)
