"""
通知模块
"""
from .telegram import (
    TelegramNotifier,
    send_notifications,
    send_single_notification,
)

__all__ = [
    "TelegramNotifier",
    "send_notifications",
    "send_single_notification",
]
