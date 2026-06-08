from __future__ import annotations

import json
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from config import Settings


DRIVE_SCOPE = ["https://www.googleapis.com/auth/drive.file"]


class GoogleDriveUploader:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @property
    def is_configured(self) -> bool:
        has_credentials = bool(self.settings.google_application_credentials_json or self.settings.google_service_account_file)
        return bool(has_credentials and self.settings.google_drive_folder_id)

    def upload_files(self, paths: list[Path]) -> dict[str, str]:
        if not self.is_configured:
            raise RuntimeError("Google Drive service account credentials or GOOGLE_DRIVE_FOLDER_ID are missing.")
        service = self._service()
        links: dict[str, str] = {"folder": f"https://drive.google.com/drive/folders/{self.settings.google_drive_folder_id}"}
        for path in paths:
            links[path.name] = self._upload_file(service, path)
        return links

    def _service(self):
        credentials = self._credentials()
        return build("drive", "v3", credentials=credentials, cache_discovery=False)

    def _credentials(self):
        if self.settings.google_application_credentials_json:
            info = json.loads(self.settings.google_application_credentials_json)
            return service_account.Credentials.from_service_account_info(info, scopes=DRIVE_SCOPE)
        return service_account.Credentials.from_service_account_file(self.settings.google_service_account_file, scopes=DRIVE_SCOPE)

    def _upload_file(self, service, path: Path) -> str:
        metadata = {"name": path.name, "parents": [self.settings.google_drive_folder_id]}
        media = MediaFileUpload(str(path), mimetype=self._mime_type(path), resumable=True)
        uploaded = service.files().create(body=metadata, media_body=media, fields="id, webViewLink").execute()
        return uploaded.get("webViewLink", f"https://drive.google.com/file/d/{uploaded['id']}/view")

    @staticmethod
    def _mime_type(path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return "application/pdf"
        if suffix == ".md":
            return "text/markdown"
        if suffix == ".csv":
            return "text/csv"
        return "application/octet-stream"
