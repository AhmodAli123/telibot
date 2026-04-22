import logging
from functools import wraps
from aiogram.types import Message, CallbackQuery
from config import Config

logger = logging.getLogger(__name__)


def maintenance_check(handler):
    @wraps(handler)
    async def wrapper(event: Message | CallbackQuery, *args, **kwargs):
        user_id = getattr(event, "from_user", None) and event.from_user.id
        if Config.MAINTENANCE_MODE and user_id not in Config.ADMIN_IDS:
            return await event.answer("🚧 রক্ষণাবেক্ষণ মোড। পরে চেষ্টা করুন।")
        return await handler(event, *args, **kwargs)
    return wrapper


def banned_check(handler):
    @wraps(handler)
    async def wrapper(event: Message | CallbackQuery, *args, **kwargs):
        user_id = getattr(event, "from_user", None) and event.from_user.id
        if user_id and user_id in Config.BANNED_USERS:
            return await event.answer("🚷 আপনাকে ব্যান করা হয়েছে।")
        return await handler(event, *args, **kwargs)
    return wrapper


def admin_only(handler):
    @wraps(handler)
    async def wrapper(event: Message | CallbackQuery, *args, **kwargs):
        user_id = getattr(event, "from_user", None) and event.from_user.id
        if user_id not in Config.ADMIN_IDS:
            return await event.answer("⛔ শুধুমাত্র অ্যাডমিন।")
        return await handler(event, *args, **kwargs)
    return wrapper


def log_action(name: str):
    def decorator(handler):
        @wraps(handler)
        async def wrapper(event: Message | CallbackQuery, *args, **kwargs):
            uid = getattr(event, "from_user", None) and event.from_user.id
            txt = getattr(event, "text", getattr(event, "data", ""))
            logger.info(f"[{name}] user={uid} payload={txt}")
            return await handler(event, *args, **kwargs)
        return wrapper
    return decorator