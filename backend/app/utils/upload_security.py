"""Shared safeguards for CSV uploads.

Uploads are intentionally bounded before pandas receives the data. This keeps the
Alpha workflow predictable and prevents an accidentally large file from being
read into memory without a clear limit.
"""

from __future__ import annotations

from fastapi import UploadFile


MAX_CSV_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_CSV_ROWS = 5_000
MAX_CSV_COLUMNS = 100

ALLOWED_CSV_CONTENT_TYPES = {
    "application/csv",
    "application/octet-stream",
    "application/vnd.ms-excel",
    "text/comma-separated-values",
    "text/csv",
    "text/plain",
}


def validate_csv_upload_metadata(file: UploadFile) -> None:
    """Validate the filename and browser-supplied media type."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise ValueError("Upload must be a .csv file.")

    content_type = (file.content_type or "").lower().split(";", 1)[0].strip()
    if content_type and content_type not in ALLOWED_CSV_CONTENT_TYPES:
        raise ValueError(
            f"Unsupported CSV media type '{content_type}'. Upload a text/csv file."
        )


async def read_limited_csv_upload(file: UploadFile) -> bytes:
    """Read no more than the configured CSV limit plus one detection byte."""
    validate_csv_upload_metadata(file)
    file_bytes = await file.read(MAX_CSV_UPLOAD_BYTES + 1)
    if len(file_bytes) > MAX_CSV_UPLOAD_BYTES:
        limit_mb = MAX_CSV_UPLOAD_BYTES // (1024 * 1024)
        raise ValueError(f"CSV exceeds the {limit_mb} MB upload limit.")
    if not file_bytes:
        raise ValueError("Uploaded CSV file is empty.")
    return file_bytes
