"""Milestone 19A controlled persistence for approved Circular Core draft imports."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app import crud, schemas


GOVERNANCE_NOTE = (
    "Controlled draft import persistence saves operator-approved draft rows into SQLite only. "
    "It does not run recommendations, verify savings, verify diversion, confirm supplier compliance, "
    "verify carbon reduction or prove environmental benefit."
)


def _normalise_text(value: str | None, fallback: str) -> str:
    text = str(value or "").strip()
    return text or fallback


def _draft_row_to_stream(row: schemas.FlexibleCircularCoreDraftRow) -> schemas.IndustrialStreamCreate:
    """Convert a claim-safe draft row into the existing IndustrialStream create schema."""
    return schemas.IndustrialStreamCreate(
        stream_id=_normalise_text(row.stream_id, f"DRAFT-{row.source_row_number}"),
        stream_name=_normalise_text(row.stream_name, "Unnamed draft stream"),
        material=_normalise_text(row.material, "Unknown material"),
        source_process=_normalise_text(row.source_process, "Unknown source process"),
        monthly_quantity_kg=float(row.monthly_quantity_kg or 0),
        current_route=_normalise_text(row.current_route, "Unknown current route"),
        disposal_cost_per_month=float(row.disposal_cost_per_month or 0),
        contamination_risk=_normalise_text(row.contamination_risk, "unknown"),
        hazardous_flag=_normalise_text(row.hazardous_flag, "unknown"),
        department=_normalise_text(row.department, "unspecified"),
        supplier=_normalise_text(row.supplier, "unspecified"),
        supplier_takeback_available=_normalise_text(row.supplier_takeback_available, "unknown"),
        recycled_content_available=_normalise_text(row.recycled_content_available, "unknown"),
        notes=_normalise_text(row.notes, "Imported from controlled draft preview. Review source evidence before claims."),
    )


def _validate_commit_request(payload: schemas.CircularCoreDraftImportCommitRequest) -> None:
    report = payload.draft_import_report

    if not payload.operator_approval:
        raise ValueError("Operator approval is required before draft rows can be saved to SQLite.")

    if not payload.replace_existing_streams:
        raise ValueError("Milestone 19A only supports controlled replacement import. Append/merge import is not available yet.")

    if report.import_status == "blocked" or report.blocking_errors:
        raise ValueError("Blocked draft import reports cannot be saved. Resolve blocking errors and rebuild the preview first.")

    if report.import_status not in {"ready", "ready_with_warnings"}:
        raise ValueError(f"Unsupported draft import status for persistence: {report.import_status}")

    if not report.draft_rows:
        raise ValueError("Draft import report does not contain any rows to save.")

    if report.draft_row_count != len(report.draft_rows):
        raise ValueError("Draft row count does not match the number of supplied draft rows.")

    stream_ids = [str(row.stream_id or "").strip() for row in report.draft_rows]
    if any(not stream_id for stream_id in stream_ids):
        raise ValueError("Every draft row must have a stream_id before persistence.")

    duplicate_stream_ids = sorted({stream_id for stream_id in stream_ids if stream_ids.count(stream_id) > 1})
    if duplicate_stream_ids:
        raise ValueError(f"Duplicate draft stream_id values cannot be imported: {', '.join(duplicate_stream_ids)}")

    invalid_status_rows = [
        str(row.source_row_number)
        for row in report.draft_rows
        if row.draft_status != "draft_only_not_imported"
    ]
    if invalid_status_rows:
        raise ValueError(
            "Only draft_only_not_imported rows can be saved in Milestone 19A. "
            f"Invalid source rows: {', '.join(invalid_status_rows)}"
        )


def import_circular_core_draft_rows(
    db: Session,
    payload: schemas.CircularCoreDraftImportCommitRequest,
) -> schemas.CircularCoreDraftImportCommitResponse:
    """Persist approved draft rows as IndustrialStream records.

    This is intentionally controlled replacement persistence only. It clears stale
    recommendations through the existing bulk_replace_streams helper but does not run
    the recommendation engine or create audit records in this milestone.
    """
    _validate_commit_request(payload)

    streams = [_draft_row_to_stream(row) for row in payload.draft_import_report.draft_rows]
    rows_imported = crud.bulk_replace_streams(db, streams)

    return schemas.CircularCoreDraftImportCommitResponse(
        import_status="imported_to_sqlite",
        rows_imported=rows_imported,
        replaced_existing_streams=True,
        recommendations_cleared=True,
        imported_stream_ids=[stream.stream_id for stream in streams],
        message=(
            f"Saved {rows_imported} operator-approved draft rows to SQLite. "
            "Existing stream rows were replaced and previous recommendations were cleared. "
            "No recommendations were run."
        ),
        governance_note=GOVERNANCE_NOTE,
    )
