from datetime import datetime, timedelta
from config import Config
from database.manager import Database


class SubscriptionService:
    def __init__(self, db: Database):
        self.db = db

    async def get_plan(self, user_id: int) -> dict:
        row = await self.db.fetchone(
            "SELECT plan, plan_expiry FROM users WHERE user_id = ?", (user_id,)
        )
        if not row:
            return Config.PLANS["free"]
        plan_name, expiry = row["plan"], row["plan_expiry"]
        if expiry and datetime.fromisoformat(expiry) < datetime.now():
            plan_name = "free"
            await self.db.execute(
                "UPDATE users SET plan = 'free', plan_expiry = NULL WHERE user_id = ?",
                (user_id,)
            )
        return Config.PLANS.get(plan_name, Config.PLANS["free"])

    async def get_plan_name(self, user_id: int) -> str:
        row = await self.db.fetchone("SELECT plan FROM users WHERE user_id = ?", (user_id,))
        return row["plan"] if row else "free"

    async def set_plan(self, user_id: int, plan: str, days: int = 30):
        expiry = (datetime.now() + timedelta(days=days)).isoformat()
        await self.db.execute(
            "UPDATE users SET plan = ?, plan_expiry = ? WHERE user_id = ?",
            (plan, expiry, user_id)
        )

    async def check_limits(self, user_id: int, files: int = 0, procs: int = 0) -> tuple[bool, str]:
        plan = await self.get_plan(user_id)
        row = await self.db.fetchone(
            "SELECT total_files, running_processes FROM users WHERE user_id = ?", (user_id,)
        )
        u_files, u_procs = row["total_files"], row["running_processes"] if row else (0, 0)

        if files and u_files + files > plan["max_files"]:
            return False, f"❌ ফাইল লিমিট ({plan['max_files']}) পূর্ণ।"
        if procs and u_procs + procs > plan["max_processes"]:
            return False, f"❌ প্রসেস লিমিট ({plan['max_processes']}) পূর্ণ।"
        return True, "OK"