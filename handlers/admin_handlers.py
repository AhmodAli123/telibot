import os
import asyncio
import html
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from database.manager import Database
from services.stats_service import StatsService
from services.process_manager import ProcessManager
from services.user_service import UserService
from utils.decorators import admin_only, log_action
from config import Config

router = Router()


@router.message(Command("admin"))
@admin_only
async def admin_panel(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📢 ব্রডকাস্ট"), KeyboardButton(text="👤 ইউজার ম্যানেজ")],
            [KeyboardButton(text="🖥️ সিস্টেম স্ট্যাটস"), KeyboardButton(text="🔄 রিস্টার্ট বট")],
            [KeyboardButton(text="🧹 লগ ক্লিয়ার"), KeyboardButton(text="🔒 বট লক/আনলক")],
            [KeyboardButton(text="🛑 ফোর্স স্টপ"), KeyboardButton(text="💻 শেল")],
            [KeyboardButton(text="◀️ মেইন মেনু")]
        ],
        resize_keyboard=True
    )
    await message.answer("🛠️ <b>অ্যাডমিন প্যানেল</b>", reply_markup=kb)


@router.message(F.text == "🖥️ সিস্টেম স্ট্যাটস")
@admin_only
async def admin_stats(message: Message, db: Database):
    st = StatsService(db)
    s = await st.get_system_stats()
    g = await st.get_global_stats()
    await message.answer(
        f"🌐 <b>গ্লোবাল স্ট্যাটস</b>\n"
        f"👥 মোট ইউজার: {g['total_users']}\n"
        f"⚙️ রানিং প্রসেস: {g['running_processes']}\n"
        f"🖥️ CPU: {s['cpu']}%\n"
        f"💾 RAM: {s['ram_used']} / {s['ram_total']} MB\n"
        f"💿 Disk: {s['disk_used']} / {s['disk_total']} MB"
    )


@router.message(F.text == "🔒 বট লক/আনলক")
@admin_only
async def toggle_lock(message: Message):
    Config.MAINTENANCE_MODE = not Config.MAINTENANCE_MODE
    status = "🔒 LOCKED" if Config.MAINTENANCE_MODE else "🔓 UNLOCKED"
    await message.answer(f"🛡️ বর্তমান স্ট্যাটাস: {status}")


@router.message(F.text == "💻 শেল")
@admin_only
@log_action("shell")
async def shell_cmd(message: Message):
    await message.answer(
        "⚠️ শেল কমান্ড পাঠান:\n/shell <command>\n"
        "অনুমোদিত: ls, ps, df, free, cat, echo, whoami, pwd, git, pip, npm, top"
    )


@router.message(Command("shell"))
@admin_only
async def exec_shell(message: Message):
    cmd = message.text.replace("/shell", "").strip()
    allowed = ("ls", "ps", "df", "free", "cat", "echo", "whoami", "pwd", "git", "pip", "npm", "top")
    if not any(cmd.startswith(a) for a in allowed):
        return await message.answer("🚫 কমান্ড অনুমোদিত নয়।")
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    out = (stdout or b"").decode()[:3000] + (stderr or b"").decode()[:3000]
    out = html.escape(out)
    await message.answer(f"<pre>{out}</pre>")


@router.message(F.text == "📢 ব্রডকাস্ট")
@admin_only
async def broadcast_prompt(message: Message):
    await message.answer("📢 ব্রডকাস্ট পাঠান:\n/broadcast <message>")


@router.message(Command("broadcast"))
@admin_only
async def broadcast_send(message: Message, db: Database):
    text = message.text.replace("/broadcast", "").strip()
    rows = await db.fetchall("SELECT user_id FROM users")
    sent = 0
    from core.bot import bot
    for row in rows:
        try:
            await bot.send_message(row["user_id"], f"📢 <b>ব্রডকাস্ট:</b>\n{text}")
            sent += 1
        except Exception:
            pass
    await message.answer(f"✅ {sent} জনকে পাঠানো হয়েছে।")


@router.message(F.text == "🛑 ফোর্স স্টপ")
@admin_only
async def force_stop_prompt(message: Message):
    await message.answer("🛑 ব্যবহার:\n/killforce <pid>")


@router.message(Command("ban"))
@admin_only
async def ban_user(message: Message, db: Database):
    args = message.text.split()
    if len(args) < 2:
        return await message.answer("ব্যবহার: /ban <user_id> [reason]")
    uid = int(args[1])
    reason = " ".join(args[2:]) if len(args) > 2 else "Admin action"
    await db.execute("INSERT OR REPLACE INTO bans (user_id, reason) VALUES (?, ?)", (uid, reason))
    Config.BANNED_USERS.add(uid)
    await message.answer(f"🚫 ইউজার {uid} ব্যান হয়েছে।")


@router.message(Command("unban"))
@admin_only
async def unban_user(message: Message, db: Database):
    args = message.text.split()
    if len(args) < 2:
        return await message.answer("ব্যবহার: /unban <user_id>")
    uid = int(args[1])
    await db.execute("DELETE FROM bans WHERE user_id = ?", (uid,))
    Config.BANNED_USERS.discard(uid)
    await message.answer(f"✅ ইউজার {uid} আনব্যান হয়েছে।")


@router.message(F.text == "🔄 রিস্টার্ট বট")
@admin_only
async def restart_bot(message: Message):
    await message.answer("♻️ বট রিস্টার্ট হচ্ছে...")
    import sys
    sys.exit(0)


@router.message(F.text == "🧹 লগ ক্লিয়ার")
@admin_only
async def clear_logs(message: Message):
    for root, dirs, files in os.walk(Config.LOGS_BASE):
        for f in files:
            os.remove(os.path.join(root, f))
    await message.answer("🧹 লগ ক্লিয়ার হয়েছে।")