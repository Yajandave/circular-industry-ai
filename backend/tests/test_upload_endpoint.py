"""CSV upload checks for Milestone 5."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.utils import upload_security

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


def test_upload_rejects_unsupported_media_type_even_with_csv_extension():
    response = client.post(
        "/api/streams/upload-csv",
        files={"file": ("not-really.csv", b"%PDF", "application/pdf")},
    )

    assert response.status_code == 400
    assert "media type" in response.json()["detail"].lower()


def test_upload_rejects_blank_required_values_without_replacing_data():
    client.post("/api/streams/load-sample")
    before = client.get("/api/streams/summary").json()
    invalid_csv = SAMPLE_CSV.read_text(encoding="utf-8").replace(",metals,", ",,", 1)

    response = client.post(
        "/api/streams/upload-csv",
        files={"file": ("missing-material.csv", invalid_csv.encode("utf-8"), "text/csv")},
    )

    assert response.status_code == 400
    assert "missing required values" in response.json()["detail"].lower()
    assert client.get("/api/streams/summary").json() == before


def test_upload_rejects_file_above_configured_limit(monkeypatch):
    monkeypatch.setattr(upload_security, "MAX_CSV_UPLOAD_BYTES", 16)

    response = client.post(
        "/api/streams/upload-csv",
        files={"file": ("too-large.csv", b"x" * 17, "text/csv")},
    )

    assert response.status_code == 400
    assert "upload limit" in response.json()["detail"].lower()


def test_custom_upload_creates_only_the_correct_dataset_audit_event():
    before = client.get("/api/audit/events?limit=500").json()
    before_max_id = max((event["id"] for event in before), default=0)

    with SAMPLE_CSV.open("rb") as file_handle:
        response = client.post(
            "/api/streams/upload-csv",
            files={"file": ("custom-industrial-data.csv", file_handle, "text/csv")},
        )

    assert response.status_code == 200
    after = client.get("/api/audit/events?limit=500").json()
    new_events = [event for event in after if event["id"] > before_max_id]
    assert len(new_events) == 1
    assert new_events[0]["event_type"] == "dataset_uploaded"
    assert new_events[0]["entity_id"] == "custom-industrial-data.csv"
    assert new_events[0]["action"] == "upload_csv_dataset"
