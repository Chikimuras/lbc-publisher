from __future__ import annotations

from dataclasses import dataclass
import os
import re

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from .settings import get_settings

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
]


@dataclass(frozen=True)
class DriveFile:
    file_id: str
    name: str
    mime_type: str


def _creds() -> Credentials:
    settings = get_settings()
    return Credentials.from_service_account_file(
        settings.google_service_account_json, scopes=SCOPES
    )


def extract_drive_folder_id(url: str) -> str | None:
    """
    Support common Drive folder URL formats.
    """
    u = (url or "").strip()
    if not u:
        return None

    # https://drive.google.com/drive/folders/<ID>
    m = re.search(r"/folders/([a-zA-Z0-9_-]+)", u)
    if m:
        return m.group(1)

    # https://drive.google.com/open?id=<ID>
    m = re.search(r"[?&]id=([a-zA-Z0-9_-]+)", u)
    if m:
        return m.group(1)

    return None


def list_images_in_folder(folder_id: str) -> list[DriveFile]:
    service = build("drive", "v3", credentials=_creds())

    q = (
        f"'{folder_id}' in parents and trashed=false and "
        "(mimeType contains 'image/')"
    )
    res = (
        service.files()
        .list(
            q=q,
            fields="files(id,name,mimeType)",
            pageSize=50,
        )
        .execute()
    )

    files = res.get("files", [])
    out = [DriveFile(f["id"], f["name"], f.get("mimeType", "")) for f in files]
    # Keep a stable order
    out.sort(key=lambda x: x.name.lower())
    return out


def download_file(file_id: str, dst_path: str) -> None:
    service = build("drive", "v3", credentials=_creds())
    request = service.files().get_media(fileId=file_id)

    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    with open(dst_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
