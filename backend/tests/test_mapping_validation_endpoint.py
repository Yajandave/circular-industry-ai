from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_validate_mapping_endpoint_returns_ready_report():
    payload = {
        "target_workspace": "circular-core",
        "mappings": [
            {"source_column": "Waste Material", "target_role": "material", "mapping_state": "accepted_by_user", "confidence": 96, "user_confirmed": True},
            {"source_column": "Monthly Weight", "target_role": "quantity", "mapping_state": "accepted_by_user", "confidence": 91, "user_confirmed": True},
            {"source_column": "Disposal Method", "target_role": "current_route", "mapping_state": "changed_by_user", "confidence": 88, "user_confirmed": True},
        ],
    }

    response = client.post("/api/data-profiler/validate-mapping", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["import_status"] == "ready"
    assert data["blocking_errors"] == []
    assert {item["role"] for item in data["resolved_required_roles"]} == {"material", "quantity", "current_route"}


def test_validate_mapping_endpoint_returns_blocked_report_for_unconfirmed_required_role():
    payload = {
        "target_workspace": "circular-core",
        "mappings": [
            {"source_column": "Waste Material", "target_role": "material", "mapping_state": "accepted_by_user", "confidence": 96, "user_confirmed": True},
            {"source_column": "Monthly Weight", "target_role": "quantity", "mapping_state": "suggested_by_system", "confidence": 91, "user_confirmed": False},
            {"source_column": "Disposal Method", "target_role": "current_route", "mapping_state": "accepted_by_user", "confidence": 88, "user_confirmed": True},
        ],
    }

    response = client.post("/api/data-profiler/validate-mapping", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["import_status"] == "blocked"
    assert any(error["code"] == "required_role_not_confirmed" for error in data["blocking_errors"])


def test_validate_mapping_endpoint_returns_bad_request_for_unknown_workspace():
    payload = {
        "target_workspace": "unknown",
        "mappings": [],
    }

    response = client.post("/api/data-profiler/validate-mapping", json=payload)

    assert response.status_code == 400
    assert "unknown target workspace" in response.json()["detail"].lower()
