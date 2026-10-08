"""Regression tests for pre-review audit and data-integrity hardening."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app import crud, models, schemas
from app.database import Base, get_db
from app.main import app
from app.utils.upload_security import MAX_CSV_UPLOAD_BYTES


@pytest.fixture()
def isolated_client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            yield client, TestingSession
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def _stream(stream_id: str, *, name: str = "Test metal") -> schemas.IndustrialStreamCreate:
    return schemas.IndustrialStreamCreate(
        stream_id=stream_id,
        stream_name=name,
        material="metals",
        source_process="test process",
        monthly_quantity_kg=100.0,
        current_route="mixed recycling",
        disposal_cost_per_month=50.0,
        contamination_risk="low",
        hazardous_flag="false",
        department="operations",
        supplier="Test Supplier",
        supplier_takeback_available="no",
        recycled_content_available="yes",
        notes="test record",
    )


def test_dataset_upload_records_only_the_real_upload_event(isolated_client):
    client, _ = isolated_client
    csv_bytes = b"""stream_id,stream_name,material,source_process,monthly_quantity_kg,current_route,disposal_cost_per_month,contamination_risk,hazardous_flag,department,supplier,supplier_takeback_available,recycled_content_available,notes
T001,Steel trim,metals,pressing,100,recycling,50,low,false,operations,Example Supplier,no,yes,clean test stream
"""

    response = client.post(
        "/api/streams/upload-csv",
        files={"file": ("custom.csv", csv_bytes, "text/csv")},
    )
    assert response.status_code == 200

    events = client.get("/api/audit/events").json()
    assert len(events) == 1
    assert events[0]["event_type"] == "dataset_uploaded"
    assert events[0]["entity_id"] == "custom.csv"
    assert events[0]["action"] == "upload_csv_dataset"
    assert not any(
        event["event_type"] == "dataset_loaded" and event["entity_id"] == "sample"
        for event in events
    )


def test_manual_audit_event_creation_is_disabled_by_default(isolated_client, monkeypatch):
    client, _ = isolated_client
    monkeypatch.delenv("ALLOW_MANUAL_AUDIT_EVENTS", raising=False)

    response = client.post(
        "/api/audit/events",
        json={
            "event_type": "manual_test",
            "entity_type": "test",
            "entity_id": "T001",
            "actor_type": "operator",
            "actor_id": "tester",
            "source": "test",
            "action": "manual_write",
            "summary": "Attempted manual audit write.",
            "decision_source": "operator_action",
            "claim_boundary": "Test only.",
            "metadata_json": {},
        },
    )

    assert response.status_code == 403
    assert "disabled" in response.json()["detail"].lower()


def test_failed_atomic_replacement_preserves_previous_dataset_and_audit_state(isolated_client):
    _, TestingSession = isolated_client

    with TestingSession() as db:
        db.add(models.IndustrialStream(**_stream("OLD001", name="Existing stream").model_dump()))
        db.commit()

        duplicate_streams = [
            _stream("DUP001", name="Duplicate one"),
            _stream("DUP001", name="Duplicate two"),
        ]

        with pytest.raises(IntegrityError):
            crud.replace_streams_with_audit_event(
                db,
                duplicate_streams,
                event_type="dataset_uploaded",
                entity_type="dataset",
                entity_id="broken.csv",
                actor_type="operator",
                actor_id="local_user",
                source="test",
                action="upload_csv_dataset",
                summary="This transaction should fail.",
                decision_source="operator_action",
                claim_boundary="No claim.",
                metadata={"filename": "broken.csv"},
            )

        remaining_ids = list(db.scalars(select(models.IndustrialStream.stream_id)).all())
        audit_count = db.scalar(select(func.count(models.AuditEvent.id))) or 0

        assert remaining_ids == ["OLD001"]
        assert audit_count == 0


def test_upload_rejects_unsupported_media_type(isolated_client):
    client, _ = isolated_client
    response = client.post(
        "/api/streams/upload-csv",
        files={"file": ("custom.csv", b"not,a,real,csv\n1,2,3,4\n", "application/pdf")},
    )
    assert response.status_code == 400
    assert "media type" in response.json()["detail"].lower()


def test_upload_rejects_files_over_size_limit(isolated_client):
    client, _ = isolated_client
    oversized = b"x" * (MAX_CSV_UPLOAD_BYTES + 1)
    response = client.post(
        "/api/streams/upload-csv",
        files={"file": ("oversized.csv", oversized, "text/csv")},
    )
    assert response.status_code == 400
    assert "upload limit" in response.json()["detail"].lower()


def test_upload_rejects_duplicate_stream_ids_before_persistence(isolated_client):
    client, TestingSession = isolated_client
    csv_bytes = b"""stream_id,stream_name,material,source_process,monthly_quantity_kg,current_route,disposal_cost_per_month,contamination_risk,hazardous_flag,department,supplier,supplier_takeback_available,recycled_content_available,notes
D001,Steel one,metals,pressing,100,recycling,50,low,false,operations,Example Supplier,no,yes,clean
D001,Steel two,metals,pressing,120,recycling,60,low,false,operations,Example Supplier,no,yes,clean
"""
    response = client.post(
        "/api/streams/upload-csv",
        files={"file": ("duplicates.csv", csv_bytes, "text/csv")},
    )
    assert response.status_code == 400
    assert "duplicate stream_id" in response.json()["detail"]

    with TestingSession() as db:
        stream_count = db.scalar(select(func.count(models.IndustrialStream.id))) or 0
        audit_count = db.scalar(select(func.count(models.AuditEvent.id))) or 0
        assert stream_count == 0
        assert audit_count == 0
