from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _ready_payload():
    return {
        "mapping_validation": {
            "target_workspace": "circular-core",
            "mappings": [
                {"source_column": "Stream ID", "target_role": "stream_id", "mapping_state": "accepted_by_user", "confidence": 90, "user_confirmed": True},
                {"source_column": "Waste Material", "target_role": "material", "mapping_state": "accepted_by_user", "confidence": 99, "user_confirmed": True},
                {"source_column": "Monthly Weight", "target_role": "quantity", "mapping_state": "accepted_by_user", "confidence": 96, "user_confirmed": True},
                {"source_column": "Weight Unit", "target_role": "quantity_unit", "mapping_state": "accepted_by_user", "confidence": 86, "user_confirmed": True},
                {"source_column": "Disposal Method", "target_role": "current_route", "mapping_state": "accepted_by_user", "confidence": 99, "user_confirmed": True},
                {"source_column": "Waste Stream", "target_role": "stream_name", "mapping_state": "accepted_by_user", "confidence": 86, "user_confirmed": True},
                {"source_column": "Monthly Disposal Cost", "target_role": "disposal_cost_per_month", "mapping_state": "accepted_by_user", "confidence": 86, "user_confirmed": True},
            ],
        },
        "source_rows": [
            {
                "Stream ID": "S001",
                "Waste Stream": "Steel offcuts",
                "Waste Material": "Steel",
                "Monthly Weight": "1250",
                "Weight Unit": "kg",
                "Disposal Method": "Recycling",
                "Monthly Disposal Cost": "780",
            }
        ],
    }


def test_build_circular_core_draft_import_endpoint_returns_ready_draft_rows():
    response = client.post("/api/data-profiler/build-circular-core-draft-import", json=_ready_payload())

    assert response.status_code == 200
    data = response.json()
    assert data["import_status"] == "ready"
    assert data["draft_row_count"] == 1
    assert data["source_row_count"] == 1
    assert data["draft_rows"][0]["stream_id"] == "S001"
    assert data["draft_rows"][0]["material"] == "Steel"
    assert data["draft_rows"][0]["monthly_quantity_kg"] == 1250
    assert data["draft_rows"][0]["current_route"] == "Recycling"
    assert data["draft_rows"][0]["draft_status"] == "draft_only_not_imported"
    assert data["blocking_errors"] == []


def test_build_circular_core_draft_import_endpoint_returns_blocked_report_for_unconfirmed_required_role():
    payload = _ready_payload()
    payload["mapping_validation"]["mappings"] = [
        {"source_column": "Waste Material", "target_role": "material", "mapping_state": "accepted_by_user", "confidence": 99, "user_confirmed": True},
        {"source_column": "Monthly Weight", "target_role": "quantity", "mapping_state": "accepted_by_user", "confidence": 96, "user_confirmed": True},
        {"source_column": "Disposal Method", "target_role": "current_route", "mapping_state": "suggested_by_system", "confidence": 99, "user_confirmed": False},
    ]

    response = client.post("/api/data-profiler/build-circular-core-draft-import", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["import_status"] == "blocked"
    assert data["draft_rows"] == []
    assert any(error["code"] == "required_role_not_confirmed" for error in data["blocking_errors"])


def test_build_circular_core_draft_import_endpoint_returns_row_warnings():
    payload = _ready_payload()
    payload["source_rows"][0]["Monthly Weight"] = "not known"
    payload["source_rows"][0]["Monthly Disposal Cost"] = "not available"

    response = client.post("/api/data-profiler/build-circular-core-draft-import", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["import_status"] == "ready_with_warnings"
    assert data["draft_rows"][0]["monthly_quantity_kg"] == 0
    assert any(warning["code"] == "invalid_quantity" for warning in data["row_warnings"])
    assert any(warning["code"] == "invalid_numeric_value" for warning in data["row_warnings"])
