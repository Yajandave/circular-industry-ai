"""CSV upload checks for Milestone 5."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_CSV = PROJECT_ROOT / "data" / "sample_industrial_streams.csv"


def test_upload_csv_replaces_streams():
    with SAMPLE_CSV.open("rb") as file_handle:
        response = client.post(
            "/api/streams/upload-csv",
            files={"file": ("sample_industrial_streams.csv", file_handle, "text/csv")},
        )

    assert response.status_code == 200
    assert response.json()["loaded_rows"] >= 40

    streams_response = client.get("/api/streams?limit=500")
    assert streams_response.status_code == 200
    assert len(streams_response.json()) >= 40


def test_upload_rejects_non_csv_file():
    response = client.post(
        "/api/streams/upload-csv",
        files={"file": ("not_a_csv.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400
    assert "csv" in response.json()["detail"].lower()
