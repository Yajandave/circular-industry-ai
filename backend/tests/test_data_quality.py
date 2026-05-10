"""Data quality and CSV validation tests."""

from io import BytesIO

from fastapi.testclient import TestClient

from app.data_quality import build_data_quality_report
from app.main import app

client = TestClient(app)


def test_data_quality_report_flags_invalid_records():
    records = [
        {
            "stream_id": "S001",
            "stream_name": "Bad stream",
            "material": "plastics",
            "source_process": "Moulding",
            "monthly_quantity_kg": 0,
            "current_route": "landfill",
            "disposal_cost_per_month": -1,
            "contamination_risk": "very dirty",
            "hazardous_flag": "unknown",
            "department": "Production",
            "supplier": "Various Suppliers",
            "supplier_takeback_available": "maybe",
            "recycled_content_available": "unknown",
        }
    ]

    report = build_data_quality_report(records, dataset_label="test")
    assert report.total_records == 1
    assert report.critical_issue_count >= 2
    assert report.warning_issue_count >= 2
    assert report.readiness_status.startswith("blocked")


def test_current_data_quality_after_sample_load(monkeypatch):
    monkeypatch.setenv("AI_REASONING_ENABLED", "false")
    load_response = client.post("/api/streams/load-sample")
    assert load_response.status_code == 200

    response = client.get("/api/data-quality/current")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_records"] == 50
    assert "readiness_status" in payload
    assert "governance_note" in payload


def test_validate_csv_rejects_missing_required_columns():
    bad_csv = b"stream_id,stream_name\nS001,Missing columns\n"
    response = client.post(
        "/api/data-quality/validate-csv",
        files={"file": ("bad.csv", BytesIO(bad_csv), "text/csv")},
    )
    assert response.status_code == 400
    assert "missing required columns" in response.json()["detail"].lower()
