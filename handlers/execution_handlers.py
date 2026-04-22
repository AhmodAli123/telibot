from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from database.manager import Database
from services.execution_service import ExecutionService
from services.process_manager import ProcessManager
from services.file_service import FileService
from services.log_service import LogService
from services.dependency_service import DependencyService
from services.subscription_service import SubscriptionService
from utils.decorators import banned_check
from utils.keyboards import back_button
from config import Config
import html

router = Router()


def _exec_svc(db: Database):
    fs = FileService(Config.STORAGE_BASE, db)
    pm = ProcessManager(db)
    ls = LogService(Config.LOGS_BASE)
    ds = DependencyService(db)
    return ExecutionService(db, fs, pm, ls, ds)


@router.message(Command("run"))
@banned_check
async def run_cmd(message: Message, db: Database):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("ব্যবহার: /run filename.py")
        return
    script = args[1]

    # Public URL port allocation if plan allows
    plan = await SubscriptionService(db).get_plan(message.from_user.id)
    port = None
    if plan.get("can_public_url"):
        from services.public_url_service import PublicURLService
        pub = PublicURLService()
        port = pub.allocate_port(message.from_user.id, script)

    svc = _exec_svc(db)
    ok, msg = await svc.run_script(message.from_user.id, script, env_port=port)
    await message.answer(msg, reply_markup=back_button())


@router.message(Command("kill"))
@banned_check
async def kill_cmd(message: Message, db: Database):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("ব্যবহার: /kill <pid> (অথবা /killforce <pid>)")
        return
    pid = int(args[1])
    force = message.text.startswith("/killforce")
    pm = ProcessManager(db)
    # ownership check
    row = await db.fetchone("SELECT user_id FROM processes WHERE pid = ?", (pid,))
    if not row:
        return await message.answer("❌ PID পাওয়া যায়নি।")
    if row["user_id"] != message.from_user.id and message.from_user.id not in Config.ADMIN_IDS:
        return await message.answer("⛔ আপনার প্রসেস নয়।")
    ok, msg = await pm.kill(pid, force=force)
    await message.answer(msg)


@router.message(Command("logs"))
@banned_check
async def logs_cmd(message: Message, db: Database):
    args = message.text.split()
    if len(args) < 2:
        pm = ProcessManager(db)
        procs = await pm.get_user_processes(message.from_user.id)
        txt = "📜 /logs <pid> দিন:\n" + "\n".join(
            f"• {p['script_name']} PID {p['pid']}" for p in procs
        )
        return await message.answer(txt or "কোনো প্রসেস নেই।")
    pid = int(args[1])
    row = await db.fetchone("SELECT log_file, user_id FROM processes WHERE pid = ?", (pid,))
    if not row:
        return await message.answer("❌ PID পাওয়া যায়নি।")
    if row["user_id"] != message.from_user.id and message.from_user.id not in Config.ADMIN_IDS:
        return await message.answer("⛔ অ্যাক্সেস নেই।")
    ls = LogService(Config.LOGS_BASE)
    content = await ls.read_tail(row["log_file"], lines=80)
    await message.answer(f"📜 <b>PID {pid} লগ:</b>\n<pre>{html.escape(content[:3000])}</pre>")


@router.message(Command("fix"))
@banned_check
async def fix_cmd(message: Message, db: Database):
    args = message.text.split()
    if len(args) < 2:
        return await message.answer("ব্যবহার: /fix <pid>")
    pid = int(args[1])
    row = await db.fetchone("SELECT log_file, user_id FROM processes WHERE pid = ?", (pid,))
    if not row or row["user_id"] != message.from_user.id:
        return await message.answer("⛔ অ্যাক্সেস নেই।")
    ls = LogService(Config.LOGS_BASE)
    content = await ls.read_tail(row["log_file"], lines=100)
    from services.ai_fix_engine import AIFixEngine
    suggestion = AIFixEngine().analyze(content)
    await message.answer(f"🧠 <b>AI সাজেশন:</b>\n{suggestion}")