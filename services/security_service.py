import os


class SecurityService:
    @staticmethod
    def is_path_safe(user_id: int, path: str, base_dir: str) -> bool:
        user_dir = os.path.abspath(os.path.join(base_dir, str(user_id)))
        target = os.path.abspath(path)
        return target.startswith(user_dir)

    @staticmethod
    def sanitize_filename(name: str) -> str:
        return os.path.basename(name).replace(" ", "_")