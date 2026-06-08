from config import Settings
from src.line_webhook import create_app


def test_health_route_cloud_run_ready(tmp_path):
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'test.db'}")
    client = create_app(settings).test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert response.json["runtime"] == "cloud-run-ready"


def test_webhook_alias_accepts_empty_line_events_without_secret(tmp_path):
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'test.db'}", line_channel_secret="")
    client = create_app(settings).test_client()
    response = client.post("/webhook", json={"events": []})
    assert response.status_code == 200
    assert response.data == b"ok"


def test_daily_report_requires_token_when_configured(tmp_path):
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'test.db'}", daily_report_token="secret-token")
    client = create_app(settings).test_client()
    response = client.post("/daily-report", json={})
    assert response.status_code == 401
