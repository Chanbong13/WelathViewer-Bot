from config import Settings
from pathlib import Path
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
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'test.db'}", scheduler_secret="secret-token")
    client = create_app(settings).test_client()
    response = client.post("/daily-report", json={})
    assert response.status_code == 401


def test_daily_report_accepts_scheduler_token_and_returns_links(tmp_path, monkeypatch):
    pdf = tmp_path / "Global_Stock_Briefing_2026-06-08.pdf"
    md = tmp_path / "NotebookLM_Source_Global_Stock_Briefing_2026-06-08.md"
    csv = tmp_path / "Raw_Stock_Data_2026-06-08.csv"
    for path in [pdf, md, csv]:
        path.write_text("test", encoding="utf-8")

    class FakeDailyReportService:
        def __init__(self, settings, responses):
            pass

        def generate(self, report_date=None):
            return {
                "date": "2026-06-08",
                "files": [pdf, md, csv],
                "summary": "Market bias: Neutral | Top watch: NVDA",
            }

    class FakeGoogleDriveUploader:
        is_configured = True

        def __init__(self, settings):
            pass

        def upload_files(self, paths: list[Path]):
            return {"folder": "https://drive.google.com/drive/folders/test", **{path.name: f"https://drive.test/{path.name}" for path in paths}}

    monkeypatch.setattr("src.line_webhook.DailyReportService", FakeDailyReportService)
    monkeypatch.setattr("src.line_webhook.GoogleDriveUploader", FakeGoogleDriveUploader)

    settings = Settings(database_url=f"sqlite:///{tmp_path / 'test.db'}", scheduler_secret="secret-token")
    client = create_app(settings).test_client()
    response = client.post("/daily-report", json={}, headers={"X-Scheduler-Token": "secret-token"})

    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert response.json["notebooklm_ready"] is True
    assert "Raw_Stock_Data_2026-06-08.csv" in response.json["files"]
    assert response.json["drive_links"]["folder"].endswith("/test")


def test_daily_report_returns_partial_warnings(tmp_path, monkeypatch):
    pdf = tmp_path / "Global_Stock_Briefing_2026-06-08.pdf"
    md = tmp_path / "NotebookLM_Source_Global_Stock_Briefing_2026-06-08.md"
    csv = tmp_path / "Raw_Stock_Data_2026-06-08.csv"
    for path in [pdf, md, csv]:
        path.write_text("test", encoding="utf-8")

    class FakeDailyReportService:
        def __init__(self, settings, responses):
            pass

        def generate(self, report_date=None):
            return {
                "date": "2026-06-08",
                "files": [pdf, md, csv],
                "summary": "Market bias: Neutral | Top watch:",
                "warnings": ["BAD: simulated provider failure"],
            }

    class FakeGoogleDriveUploader:
        is_configured = False

        def __init__(self, settings):
            pass

    monkeypatch.setattr("src.line_webhook.DailyReportService", FakeDailyReportService)
    monkeypatch.setattr("src.line_webhook.GoogleDriveUploader", FakeGoogleDriveUploader)

    settings = Settings(database_url=f"sqlite:///{tmp_path / 'test.db'}", scheduler_secret="secret-token")
    client = create_app(settings).test_client()
    response = client.post("/daily-report", json={}, headers={"X-Scheduler-Token": "secret-token"})

    assert response.status_code == 200
    assert "BAD: simulated provider failure" in response.json["warnings"]
    assert "Google Drive uploader is not configured." in response.json["warnings"]


def test_daily_report_keeps_json_response_when_drive_upload_fails(tmp_path, monkeypatch):
    pdf = tmp_path / "Global_Stock_Briefing_2026-06-08.pdf"
    md = tmp_path / "NotebookLM_Source_Global_Stock_Briefing_2026-06-08.md"
    csv = tmp_path / "Raw_Stock_Data_2026-06-08.csv"
    for path in [pdf, md, csv]:
        path.write_text("test", encoding="utf-8")

    class FakeDailyReportService:
        def __init__(self, settings, responses):
            pass

        def generate(self, report_date=None):
            return {
                "date": "2026-06-08",
                "files": [pdf, md, csv],
                "summary": "Market bias: Neutral | Top watch: NVDA",
                "warnings": [],
            }

    class FailingGoogleDriveUploader:
        is_configured = True

        def __init__(self, settings):
            pass

        def upload_files(self, paths):
            raise RuntimeError("drive permission denied")

    monkeypatch.setattr("src.line_webhook.DailyReportService", FakeDailyReportService)
    monkeypatch.setattr("src.line_webhook.GoogleDriveUploader", FailingGoogleDriveUploader)

    settings = Settings(database_url=f"sqlite:///{tmp_path / 'test.db'}", scheduler_secret="secret-token")
    client = create_app(settings).test_client()
    response = client.post("/daily-report", json={}, headers={"X-Scheduler-Token": "secret-token"})

    assert response.status_code == 200
    assert response.json["drive_links"] == {}
    assert "Google Drive upload failed" in response.json["warnings"][0]
