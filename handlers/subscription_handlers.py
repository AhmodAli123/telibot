from aiogram import Router, F
from aiogram.types import Message
from database.manager import Database
from services.subscription_service import SubscriptionService
from utils.decorators import banned_check

router = Router()


@router.message(F.text == "⚙️ সেটিংস")
@banned_check
async def settings(message: Message, db: Database):
    sub = SubscriptionService(db)
    name = await sub.get_plan_name(message.from_user.id)
    limits = await sub.get_plan(message.from_user.id)
    text = (
        f"⚙️ <b>সেটিংস</b>\n\n"
        f"🎫 প্ল্যান: <code>{name}</code>\n"
        f"📁 ম্যাক্স ফাইল: {limits['max_files']}\n"
        f"⚙️ ম্যাক্স প্রসেস: {limits['max_processes']}\n"
        f"💾 ম্যাক্স স্টোরেজ: {limits['max_storage_mb']} MB\n\n"
        f"আপগ্রেড করতে অ্যাডমিনের সাথে যোগাযোগ করুন।"
    )
    await message.answer(text)