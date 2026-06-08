from config import Settings
from src.google_drive_uploader import GoogleDriveUploader


def test_upload_file_enables_shared_drive_support(tmp_path):
    uploaded_path = tmp_path / "report.md"
    uploaded_path.write_text("# report", encoding="utf-8")
    calls = {}

    class FakeCreateRequest:
        def execute(self):
            return {"id": "file-id", "webViewLink": "https://drive.test/file-id"}

    class FakeFiles:
        def create(self, **kwargs):
            calls.update(kwargs)
            return FakeCreateRequest()

    class FakeService:
        def files(self):
            return FakeFiles()

    settings = Settings(google_drive_folder_id="folder-id")
    uploader = GoogleDriveUploader(settings)
    link = uploader._upload_file(FakeService(), uploaded_path)

    assert link == "https://drive.test/file-id"
    assert calls["supportsAllDrives"] is True
    assert calls["body"]["parents"] == ["folder-id"]
