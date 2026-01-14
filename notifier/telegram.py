"""
Telegram 通知模块

负责将新职位推送到 Telegram。
"""
import asyncio
import logging
from typing import Optional

import config

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Telegram 通知器"""
    
    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None
    ):
        """
        初始化 Telegram 通知器
        
        Args:
            bot_token: Bot Token（默认使用配置）
            chat_id: Chat ID（默认使用配置）
        """
        self.bot_token = bot_token or config.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or config.TELEGRAM_CHAT_ID
        self._validate_config()
    
    def _validate_config(self):
        """验证配置"""
        if not self.bot_token:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN not set. "
                "Please set it as an environment variable."
            )
        if not self.chat_id:
            raise ValueError(
                "TELEGRAM_CHAT_ID not set. "
                "Please set it as an environment variable."
            )
    
    async def send_message(self, text: str) -> bool:
        """
        发送消息
        
        Args:
            text: 消息文本（支持 HTML 格式）
        
        Returns:
            True 如果发送成功
        """
        import aiohttp
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=30) as response:
                    if response.status == 200:
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"Telegram API error: {response.status} - {error_text}"
                        )
                        return False
        
        except asyncio.TimeoutError:
            logger.error("Telegram API timeout")
            return False
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    async def send_job_notification(self, job) -> bool:
        """
        发送职位通知
        
        Args:
            job: Job 对象
        
        Returns:
            True 如果发送成功
        """
        message = job.format_telegram_message()
        return await self.send_message(message)
    
    async def send_job_notifications(
        self,
        jobs: list,
        max_messages: Optional[int] = None
    ) -> tuple[int, int]:
        """
        批量发送职位通知
        
        Args:
            jobs: Job 对象列表
            max_messages: 最大发送数量（默认使用配置）
        
        Returns:
            (成功数量, 失败数量)
        """
        max_messages = max_messages or config.MAX_MESSAGES_PER_BATCH
        
        # 限制发送数量
        jobs_to_send = jobs[:max_messages]
        
        if len(jobs) > max_messages:
            logger.warning(
                f"Too many jobs ({len(jobs)}), "
                f"only sending first {max_messages}"
            )
        
        success_count = 0
        fail_count = 0
        
        for job in jobs_to_send:
            if await self.send_job_notification(job):
                success_count += 1
            else:
                fail_count += 1
            
            # 避免触发 Telegram 速率限制
            await asyncio.sleep(config.MESSAGE_DELAY)
        
        logger.info(
            f"Sent {success_count} notifications, {fail_count} failed"
        )
        
        return success_count, fail_count
    
    async def send_summary(
        self,
        new_jobs_count: int,
        total_scraped: int,
        sources: list[str]
    ):
        """
        发送汇总消息
        
        Args:
            new_jobs_count: 新职位数量
            total_scraped: 总爬取数量
            sources: 数据源列表
        """
        if new_jobs_count == 0:
            return
        
        message = (
            f"📊 <b>Job Monitor Summary</b>\n\n"
            f"🆕 New jobs found: <b>{new_jobs_count}</b>\n"
            f"📥 Total scraped: {total_scraped}\n"
            f"📂 Sources: {', '.join(sources)}"
        )
        
        await self.send_message(message)


def send_notifications(jobs: list) -> tuple[int, int]:
    """
    同步接口：发送职位通知
    
    Args:
        jobs: Job 对象列表
    
    Returns:
        (成功数量, 失败数量)
    """
    notifier = TelegramNotifier()
    return asyncio.run(notifier.send_job_notifications(jobs))


def send_single_notification(job) -> bool:
    """
    同步接口：发送单个职位通知
    
    Args:
        job: Job 对象
    
    Returns:
        True 如果发送成功
    """
    notifier = TelegramNotifier()
    return asyncio.run(notifier.send_job_notification(job))
