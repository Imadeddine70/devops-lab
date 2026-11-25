"""Petit service HTTP servant de support au pipeline DevOps."""
import os
import threading
import time

from flask import Flask, Response, jsonify

app = Flask(__name__)

START_TIME = time.time()
_lock = threading.Lock()
_requests = {"/": 0, "/health": 0, "/api/info": 0}


def _count(path):
    with _lock:
        _requests[path] = _requests.get(path, 0) + 1


@app.get("/")
def index():
    _count("/")
    return jsonify(service="devops-lab", status="ok")


@app.get("/health")
def health():
    _count("/health")
    return jsonify(status="healthy")


@app.get("/api/info")
def info():
    _count("/api/info")
    return jsonify(
        version=os.environ.get("APP_VERSION", "dev"),
        environment=os.environ.get("APP_ENV", "local"),
        uptime_seconds=round(time.time() - START_TIME, 1),
    )


@app.get("/metrics")
def metrics():
    """Métriques au format texte Prometheus (écrit à la main, sans dépendance)."""
    lines = [
        "# HELP app_requests_total Nombre de requêtes par chemin.",
        "# TYPE app_requests_total counter",
    ]
    with _lock:
        for path, n in sorted(_requests.items()):
            lines.append(f'app_requests_total{{path="{path}"}} {n}')
    lines += [
        "# HELP app_uptime_seconds Durée de fonctionnement du service.",
        "# TYPE app_uptime_seconds gauge",
        f"app_uptime_seconds {time.time() - START_TIME:.1f}",
    ]
    return Response("\n".join(lines) + "\n", mimetype="text/plain; version=0.0.4")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
