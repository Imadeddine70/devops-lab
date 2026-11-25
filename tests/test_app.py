import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from main import app  # noqa: E402


def client():
    return app.test_client()


def test_health():
    r = client().get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "healthy"}


def test_info_uses_environment(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "1.2.3")
    monkeypatch.setenv("APP_ENV", "test")
    data = client().get("/api/info").get_json()
    assert data["version"] == "1.2.3"
    assert data["environment"] == "test"


def test_metrics_counts_requests():
    c = client()
    c.get("/health")
    body = c.get("/metrics").get_data(as_text=True)
    assert "# TYPE app_requests_total counter" in body
    assert 'app_requests_total{path="/health"}' in body
    assert "app_uptime_seconds" in body
