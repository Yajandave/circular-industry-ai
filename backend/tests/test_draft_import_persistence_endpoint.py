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
                {"source_column": "Department", "target_role": "department", "mapping_state": "accepted_by_user", "confidence": 86, "user_confirmed": True},
                {"source_column": "Supplier", "target_role": "supplier", "mapping_state": "accepted_by_user", "confidence": 86, "user_confirmed": True},
            ],
        },
        "source_rows": [
            {
                "Stream ID": "DRAFT-001",
                "Waste Stream": "Steel offcuts",
                "Waste Material": "Steel",
                "Monthly Weight": "1250",
                "Weight Unit": "kg",
                "Disposal Method": "Recycling",
                "Monthly Disposal Cost": "780",
                "Department": "Fabrication",
                "Supplier": "Example Metals",
            },
            {
                "Stream ID": "DRAFT-002",
                "Waste Stream": "Cardboard packaging",
                "Waste Material": "Cardboard",
                "Monthly Weight": "400",
                "Weight Unit": "kg",
                "Disposal Method": "General waste",
                "Monthly Disposal Cost": "120",
                "Department": "Warehouse",
                "Supplier": "Packaging Supplier",
            },
        ],
    }


def _ready_draft_report():
    response = client.post("/api/data-profiler/build-circular-core-draft-import", json=_ready_payload())
    assert response.status_code == 200
    data = response.json()
    assert data["import_status"] == "ready"
    return data


def test_import_circular_core_draft_endpoint_saves_approved_draft_rows():
    client.post("/api/streams/load-sample")
    report = _ready_draft_report()

    response = client.post(
        "/api/data-profiler/import-circular-core-draft",
        json={
            "draft_import_report": report,
            "operator_approval": True,
            "approval_note": "Approved after preview review in test.",
            "replace_existing_streams": True,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["import_status"] == "imported_to_sqlite"
    assert data["rows_imported"] == 2
    assert data["replaced_existing_streams"] is True
    assert data["recommendations_cleared"] is True
    assert data["imported_stream_ids"] == ["DRAFT-001", "DRAFT-002"]
    assert "No recommendations were run" in data["message"]

    streams_response = client.get("/api/streams?limit=500")
    assert streams_response.status_code == 200
    streams = streams_response.json()
    assert len(streams) == 2
    assert streams[0]["stream_id"] == "DRAFT-001"
    assert streams[0]["material"] == "Steel"

    summary_response = client.get("/api/streams/summary")
    assert summary_response.status_code == 200
    assert summary_response.json()["total_streams"] == 2


def test_import_circular_core_draft_endpoint_requires_operator_approval():
    report = _ready_draft_report()

    response = client.post(
        "/api/data-profiler/import-circular-core-draft",
        json={
            "draft_import_report": report,
            "operator_approval": False,
            "replace_existing_streams": True,
        },
    )

    assert response.status_code == 400
    assert "Operator approval is required" in response.json()["detail"]


def test_import_circular_core_draft_endpoint_rejects_blocked_reports():
    payload = _ready_payload()
    payload["mapping_validation"]["mappings"] = [
        {"source_column": "Waste Material", "target_role": "material", "mapping_state": "accepted_by_user", "confidence": 99, "user_confirmed": True},
        {"source_column": "Monthly Weight", "target_role": "quantity", "mapping_state": "accepted_by_user", "confidence": 96, "user_confirmed": True},
        {"source_column": "Disposal Method", "target_role": "current_route", "mapping_state": "suggested_by_system", "confidence": 99, "user_confirmed": False},
    ]

    draft_response = client.post("/api/data-profiler/build-circular-core-draft-import", json=payload)
    assert draft_response.status_code == 200
    report = draft_response.json()
    assert report["import_status"] == "blocked"

    response = client.post(
        "/api/data-profiler/import-circular-core-draft",
        json={
            "draft_import_report": report,
            "operator_approval": True,
            "replace_existing_streams": True,
        },
    )

    assert response.status_code == 400
    assert "Blocked draft import reports cannot be saved" in response.json()["detail"]


def test_import_circular_core_draft_endpoint_rejects_duplicate_stream_ids():
    report = _ready_draft_report()
    report["draft_rows"][1]["stream_id"] = "DRAFT-001"

    response = client.post(
        "/api/data-profiler/import-circular-core-draft",
        json={
            "draft_import_report": report,
            "operator_approval": True,
            "replace_existing_streams": True,
        },
    )

    assert response.status_code == 400
    assert "Duplicate draft stream_id values" in response.json()["detail"]
