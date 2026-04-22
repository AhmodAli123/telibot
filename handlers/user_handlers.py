from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from database.manager import Database
from services.user_service import UserService
from services.stats_service import StatsService
from services.subscription_service import SubscriptionService
from utils.decorators import maintenance_check, banned_check, log_action
from utils.keyboards import main_menu
from config import Config

router = Router()


@router.message(Command("start"))
@maintenance_check
@banned_check
@log_action("start")
async def cmd_start(message: Message, db: Database):
    svc = UserService(db)
    await svc.register(message.from_user.id, message.from_user.username)
    await svc.update_activity(message.from_user.id)

    is_admin = message.from_user.id in Config.ADMIN_IDS
    plan = await SubscriptionService(db).get_plan_name(message.from_user.id)
    await message.answer(
        f"👋 স্বাগতম, <b>{message.from_user.full_name}</b>!\n\n"
        f"📦 বর্তমান প্ল্যান: <code>{plan}</code>\n"
        f"ফাইল আপলোড করে স্ক্রিপ্ট রান শুরু করুন।",
        reply_markup=main_menu(is_admin)
    )


@router.message(F.text == "📊 ড্যাশবোর্ড")
@banned_check
async def dashboard(message: Message, db: Database):
    st = StatsService(db)
    u = await st.get_user_stats(message.from_user.id)
    s = await st.get_system_stats()
    text = (
        f"📊 <b>ড্যাশবোর্ড</b>\n\n"
        f"🎫 প্ল্যান: <code>{u['plan']}</code>\n"
        f"📁 ফাইল: {u['total_files']} | ⚙️ প্রসেস: {u['running_processes']}\n\n"
        f"🖥️ CPU: {s['cpu']}% | RAM: {s['ram_used']}MB / {s['ram_total']}MB\n"
        f"💿 Disk: {s['disk_used']}MB / {s['disk_total']}MB\n"
        f"⏱️ Uptime: {s['uptime']}s"
    )
    await message.answer(text)


@router.message(F.text == "❓ সাহায্য")
async def help_msg(message: Message):
    await message.answer(
        "📖 <b>সাহায্য</b>\n\n"
        "📁 ফাইল ম্যানেজার — ফাইল আপলোড / ডিলিট\n"
        "▶️ স্ক্রিপ্ট রান — /run filename.py\n"
        "⏱️ ক্রন — /cron filename.py 3600\n"
        "🔗 Git — /gitclone <url>\n"
        "📊 ড্যাশবোর্ড — তথ্য দেখুন\n"
        "🛒 মার্কেটপ্লেস — /market\n\n"
        "⚙️ স্টপ করতে: /kill <pid>\n"
        "📜 লগ দেখতে: /logs <pid>\n"
        "🧠 AI ফিক্স: /fix <pid>"
    )