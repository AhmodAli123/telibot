import socket
from flask import Flask, request, Response
import requests


class PublicURLService:
    BASE_PORT = 12000

    def __init__(self):
        self.allocations: dict[tuple[int, str], int] = {}

    def allocate_port(self, user_id: int, script_name: str) -> int:
        port = self.BASE_PORT + (user_id % 1000) + (hash(script_name) % 1000)
        while not self._is_free(port):
            port += 1
        self.allocations[(user_id, script_name)] = port
        return port

    def get_port(self, user_id: int, script_name: str) -> int | None:
        return self.allocations.get((user_id, script_name))

    def _is_free(self, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", port)) != 0

    def proxy_route(self, app: Flask):
        @app.route("/app/<user_id>/<script_name>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
        def _proxy(user_id, script_name):
            port = self.get_port(int(user_id), script_name)
            if not port:
                return "🚫 অ্যাপ চলছে না", 404
            try:
                target = f"http://127.0.0.1:{port}{request.full_path.replace(f'/app/{user_id}/{script_name}', '')}"
                resp = requests.request(
                    method=request.method,
                    url=target,
                    headers={k: v for k, v in request.headers if k.lower() != "host"},
                    data=request.get_data(),
                    timeout=10
                )
                return Response(resp.content, resp.status_code, resp.headers.items())
            except Exception as e:
                return f"Proxy Error: {e}", 502