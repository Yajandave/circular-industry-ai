"""Transaction and CSV export safety regression tests."""

from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app import crud, models, schemas
from app.database import SessionLocal
from app.utils.csv_export import protect_csv_value


def _stream(stream_id: str) -> schemas.IndustrialStreamCreate:
    return schemas.IndustrialStreamCreate(
        stream_id=stream_id,
        stream_name="Safety test stream",
        material="metals",
        source_process="test process",
        monthly_quantity_kg=10,
        current_route="recycling",
        disposal_cost_per_month=5,
        contamination_risk="low",
        hazardous_flag="false",
        department="test",
        supplier="test supplier",
        supplier_takeback_available="unknown",
        recycled_content_available="unknown",
        notes="transaction test",
    )


def test_failed_atomic_import_preserves_previous_dataset_and_skips_audit_event():
    db = SessionLocal()
    try:
        crud.replace_streams_with_audit_event(
            db,
            [_stream("SAFE-ORIGINAL")],
            event_type="dataset_uploaded",
            entity_type="dataset",
            entity_id="original.csv",
            actor_type="operator",
            actor_id="test",
            source="test",
            action="seed_test_dataset",
            summary="Seeded transaction test.",
            decision_source="test",
            claim_boundary="Test only.",
        )

        with pytest.raises(IntegrityError):
            crud.replace_streams_with_audit_event(
                db,
                [_stream("DUPLICATE"), _stream("DUPLICATE")],
                event_type="dataset_uploaded",
                entity_type="dataset",
                entity_id="failed.csv",
                actor_type="operator",
                actor_id="test",
                source="test",
                action="failed_test_import",
                summary="This transaction must roll back.",
                decision_source="test",
                claim_boundary="Test only.",
            )

        stream_ids = list(db.scalars(select(models.IndustrialStream.stream_id)).all())
        failed_event = db.scalars(
            select(models.AuditEvent).where(models.AuditEvent.entity_id == "failed.csv")
        ).first()
        assert stream_ids == ["SAFE-ORIGINAL"]
        assert failed_event is None
    finally:
        db.close()


@pytest.mark.parametrize("value", ["=SUM(A1:A2)", "+cmd", "-2+3", "@IMPORT", "  =hidden"])
def test_csv_export_text_cannot_execute_as_spreadsheet_formula(value):
    assert protect_csv_value(value).startswith("'")


def test_csv_export_preserves_normal_text_and_numbers():
    assert protect_csv_value("Steel offcuts") == "Steel offcuts"
    assert protect_csv_value(1250.0) == 1250.0
