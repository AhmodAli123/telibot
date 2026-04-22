import os
import re
import asyncio


class DependencyService:
    PACKAGE_MAP = {
        "PIL": "Pillow", "cv2": "opencv-python", "sklearn": "scikit-learn",
        "bs4": "beautifulsoup4", "telegram": "python-telegram-bot",
    }

    def __init__(self, db):
        self.db = db

    async def resolve(self, user_dir: str, language: str):
        if language == "python":
            await self._resolve_python(user_dir)
        elif language == "node":
            await self._resolve_node(user_dir)

    async def _resolve_python(self, user_dir: str):
        imports = set()
        for f in os.listdir(user_dir):
            if f.endswith(".py"):
                with open(os.path.join(user_dir, f), "r", encoding="utf-8", errors="ignore") as fp:
                    content = fp.read()
                matches = re.findall(r'^(?:import|from)\s+([a-zA-Z_][a-zA-Z0-9_]*)', content, re.MULTILINE)
                imports.update(matches)

        to_install = []
        for imp in imports:
            pkg = self.PACKAGE_MAP.get(imp, imp)
            # simple check if already in requirements
            to_install.append(pkg)

        if to_install:
            proc = await asyncio.create_subprocess_exec(
                "pip", "install", "--user", "-q", *to_install,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()

    async def _resolve_node(self, user_dir: str):
        pkg = os.path.join(user_dir, "package.json")
        if os.path.exists(pkg):
            proc = await asyncio.create_subprocess_exec(
                "npm", "install", cwd=user_dir,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()