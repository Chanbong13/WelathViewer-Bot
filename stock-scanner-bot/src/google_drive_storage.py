from __future__ import annotations

from pathlib import Path

from config import Settings
from src.google_drive_uploader import GoogleDriveUploader


class GoogleDriveStorage:
    def __init__(self, settings: Settings) -> None:
        self.uploader = GoogleDriveUploader(settings)

    def save_markdown_if_configured(self, path: Path) -> dict[str, str]:
        if not self.uploader.is_configured:
            return {}
        return self.uploader.upload_files([path])
