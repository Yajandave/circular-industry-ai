"""Conservative assessment of external regulatory waste-movement records.

This is a data-understanding layer, NOT a waste classifier, conversion into
monthly factory streams, or a circular-route recommendation engine.
"""
from __future__ import annotations

import re
from typing import Any

SOURCE_FIELDS = (
    "Waste Code", "EWC Waste Desc", "EWC Chapter", "Basic Waste Cat",
    "Form", "Fate", "R and D code", "movement",
    "Tonnes Received", "Tonnes Removed",
)
MISSING_INPUTS = (
    "measurement_period_and_stream_monthly_quantity",
    "verified_material_composition_or_grade",
    "contamination_assessment",
    "competent_hazardous_waste_classification",
    "supplier_and_receiving_route_acceptance",
    "commercial_cost_basis",
)

def _text(v: Any) -> str:
    return "" if v is None else str(v).strip()

def _reported_tonnes(row: dict[str, Any]) -> tuple[str | None, float | None, list[str]]:
    warnings: list[str] = []
    values = []
    for field in ("Tonnes Received", "Tonnes Removed"):
        raw = _text(row.get(field))
        if not raw:
            continue
        try:
            number = float(raw.replace(",", ""))
        except (TypeError, ValueError):
            warnings.append(f"{field}: unparseable tonnage")
            continue
        if not (0 <= number < float("inf")):
            warnings.append(f"{field}: negative or non-finite tonnage")
            continue
        values.append((field, number))
    if len(values) != 1:
        warnings.append("Expected exactly one reported movement quantity; cannot safely assign one.")
        return None, None, warnings
    return values[0][0], values[0][1], warnings

def assess_external_waste_row(row: dict[str, Any]) -> dict[str, Any]:
    """Keep original values and distinguish reported classification from verified facts."""
    raw = {k: row.get(k) for k in SOURCE_FIELDS if k in row}
    waste_code = _text(row.get("Waste Code"))
    description = _text(row.get("EWC Waste Desc"))
    valid_code = bool(re.fullmatch(r"\d{2}\s?\d{2}\s?\d{2}\*?", waste_code))
    hazardous_asterisk = waste_code.endswith("*") if valid_code else None
    quantity_field, tonnes, warnings = _reported_tonnes(row)
    if not valid_code:
        warnings.append("Missing or unrecognised reported waste-code format.")
    if not description:
        warnings.append("Waste description missing.")

    # EWC descriptions are text, not a validated material specification.
    return {
        "source_identifier": _text(row.get("challenge_id")) or None,
        "source_excel_row": row.get("source_excel_row"),
        "reported_waste": raw,
        "reported_waste_code": waste_code or None,
        "reported_hazardous_code_asterisk": hazardous_asterisk,
        "reported_description": description or None,
        "quantity_source_field": quantity_field,
        "reported_movement_tonnes": tonnes,
        "reported_movement_kg": round(tonnes * 1000, 3) if tonnes is not None else None,
        "monthly_stream_quantity_kg": None,
        "material_family": None,
        "material_subtype": None,
        "route_recommendation": None,
        "classification_status": "unverified_reported_waste_code_not_material_classification",
        "decision_status": "requires_mapping_and_competent_evidence_review",
        "missing_decision_inputs": list(MISSING_INPUTS),
        "warnings": warnings,
        "reason": (
            "Waste-facility movement tonnage has no proven monthly factory-stream basis. "
            "Waste-code descriptions do not establish material grade, contamination, "
            "legal classification or technically accepted circular route."
        ),
    }

def assess_external_waste_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("At least one source record is required.")
    if len(rows) > 1000:
        raise ValueError("Evaluate at most 1000 source records per request.")
    records = [assess_external_waste_row(row) for row in rows]
    return {
        "total_records": len(records),
        "recommendations_generated": 0,
        "records_requiring_review": len(records),
        "records": records,
        "governance_note": (
            "This is read-only external-data assessment, not a conversion to "
            "monthly factory streams or regulatory/technical verification."
        ),
    }
