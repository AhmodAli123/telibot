from flask import Flask, jsonify
from threading import Thread

app = Flask(__name__)
public_url_service = None

def init_public(url_svc):
    """Inject PublicURLService reverse-proxy routes."""
    global public_url_service
    public_url_service = url_svc
    if url_svc:
        url_svc.proxy_route(app)

@app.route("/")
def home():
    return jsonify({
        "status": "Telegram Cloud Code Hosting Platform is running",
        "service": "active",
        "mode": "production"
    })

@app.route("/health")
def health():
    return jsonify({"ok": True})

def run_flask(port, host):
    app.run(host=host, port=port, debug=False, use_reloader=False)

def keep_alive(port, host):
    t = Thread(target=run_flask, args=(port, host))
    t.daemon = True
    t.start()