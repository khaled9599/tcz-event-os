from __future__ import annotations

import mimetypes
import re
from pathlib import Path
from typing import Any, TypedDict

MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024
MAX_ATTACHMENTS_PER_MESSAGE = 5
MAX_EXTRACTED_TEXT_CHARS = 50_000

TEXT_EXTENSIONS = {".csv", ".json", ".md", ".txt", ".yaml", ".yml"}
BINARY_EXTENSIONS = {".docx", ".jpeg", ".jpg", ".pdf", ".png", ".pptx", ".webp", ".xlsx"}
ALLOWED_EXTENSIONS = TEXT_EXTENSIONS | BINARY_EXTENSIONS


class AttachmentRecord(TypedDict):
    attachment_id: str
    agent_id: str
    filename: str
    content_type: str
    size_bytes: int
    storage_path: str
    extracted_text: str | None
    created_at: str


def safe_filename(filename: str) -> str:
    name = Path(filename or "attachment").name.strip()
    name = re.sub(r"[^A-Za-z0-9._ -]+", "_", name)[:120]
    return name or "attachment"


def normalized_content_type(filename: str, supplied: str | None) -> str:
    guessed = mimetypes.guess_type(filename)[0]
    if supplied and supplied != "application/octet-stream":
        return supplied
    return guessed or "application/octet-stream"


def validate_attachment(filename: str, data: bytes) -> None:
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise ValueError(f"unsupported file type; allowed extensions: {allowed}")
    if not data:
        raise ValueError("attachment cannot be empty")
    if len(data) > MAX_ATTACHMENT_BYTES:
        raise ValueError("attachment exceeds the 10 MB limit")


def extract_text(filename: str, data: bytes) -> str | None:
    if Path(filename).suffix.lower() not in TEXT_EXTENSIONS:
        return None
    return data.decode("utf-8", errors="replace")[:MAX_EXTRACTED_TEXT_CHARS]


def public_attachment(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "attachment_id": record["attachment_id"],
        "filename": record["filename"],
        "content_type": record["content_type"],
        "size_bytes": record["size_bytes"],
        "text_available": bool(record.get("extracted_text")),
        "created_at": record["created_at"],
    }
