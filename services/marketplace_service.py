from database.manager import Database


class MarketplaceService:
    def __init__(self, db: Database):
        self.db = db

    async def publish(self, author_id: int, title: str, description: str, code: str, price: int = 0):
        await self.db.execute(
            "INSERT INTO marketplace (author_id, title, description, code, price) VALUES (?, ?, ?, ?, ?)",
            (author_id, title, description, code, price)
        )

    async def list_items(self):
        rows = await self.db.fetchall("SELECT * FROM marketplace ORDER BY id DESC LIMIT 20")
        return [dict(r) for r in rows]

    async def get_item(self, item_id: int):
        row = await self.db.fetchone("SELECT * FROM marketplace WHERE id = ?", (item_id,))
        return dict(row) if row else None