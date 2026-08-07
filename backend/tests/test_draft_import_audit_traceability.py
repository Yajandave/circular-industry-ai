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
                "Stream ID": "AUDIT-001",
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
                "Stream ID": "AUDIT-002",
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


def _draft_report_with_warning():
    response = client.post("/api/data-profiler/build-circular-core-draft-import", json=_ready_payload())
    assert response.status_code == 200
    report = response.json()
    assert report["import_status"] == "ready"
    return report


def test_import_circular_core_draft_creates_traceability_audit_event():
    client.post("/api/streams/load-sample")
    report = _draft_report_with_warning()

    response = client.post(
        "/api/data-profiler/import-circular-core-draft",
        json={
            "draft_import_report": report,
            "operator_approval": True,
            "approval_note": "Approved after reviewing warning test case.",
            "replace_existing_streams": True,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["import_status"] == "imported_to_sqlite"
    assert data["audit_event_created"] is True
    assert isinstance(data["audit_event_id"], int)
    assert data["traceability_note"]
    assert "traceability audit event" in data["message"]

    events_response = client.get("/api/audit/events?event_type=draft_import_committed&limit=5")
    assert events_response.status_code == 200
    events = events_response.json()
    assert events

    latest_event = events[0]
    assert latest_event["id"] == data["audit_event_id"]
    assert latest_event["event_type"] == "draft_import_committed"
    assert latest_event["entity_type"] == "circular_core_import"
    assert latest_event["action"] == "commit_approved_draft_rows"
    assert latest_event["decision_source"] == "operator_approved_draft_import"
    assert "does not verify" in latest_event["claim_boundary"]

    metadata = latest_event["metadata_json"]
    assert metadata["rows_imported"] == 2
    assert metadata["draft_row_count"] == 2
    assert metadata["source_row_count"] == 2
    assert metadata["row_warning_count"] == 0
    assert metadata["blocking_error_count"] == 0
    assert metadata["recommendations_cleared"] is True
    assert metadata["recommendations_run"] is False
    assert metadata["approval_note_present"] is True
    assert metadata["imported_stream_ids"] == ["AUDIT-001", "AUDIT-002"]
    assert metadata["warning_code_breakdown"] == {}


def test_import_circular_core_draft_audit_summary_counts_import_events():
    report = _draft_report_with_warning()

    response = client.post(
        "/api/data-profiler/import-circular-core-draft",
        json={
            "draft_import_report": report,
            "operator_approval": True,
            "replace_existing_streams": True,
        },
    )
    assert response.status_code == 200

    summary_response = client.get("/api/audit/summary")
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["event_type_breakdown"].get("draft_import_committed", 0) >= 1
    assert summary["entity_type_breakdown"].get("circular_core_import", 0) >= 1
    assert summary["decision_source_breakdown"].get("operator_approved_draft_import", 0) >= 1
