"""Flexible Circular Core import contract.

This module transforms user-confirmed mapped source rows into draft Circular Core
rows. It does not write to the database, run recommendations or verify impacts.
"""

from __future__ import annotations

from app.mapping_validation import validate_confirmed_mapping


GOVERNANCE_NOTE = (
    "Flexible import creates draft Circular Core rows from user-confirmed mappings only. "
    "It does not verify source data, savings, diversion, environmental benefit, supplier compliance, "
    "legal compliance or external sustainability claims."
)

UNKNOWN = "Unknown"


def build_flexible_circular_core_import(payload) -> dict:
    """Build draft Circular Core rows from mapped source rows without persistence."""

    validation_report = validate_confirmed_mapping(payload.mapping_validation)
    if validation_report["target_workspace"] != "circular-core":
        return _blocked_report(
            payload=payload,
            validation_report=validation_report,
            blocking_error={
                "code": "unsupported_target_workspace",
                "message": "Flexible Circular Core import only supports the circular-core workspace in this milestone.",
                "source_row_number": None,
                "source_column": None,
                "target_role": None,
            },
        )

    if validation_report["import_status"] == "blocked":
        return {
            "import_status": "blocked",
            "draft_row_count": 0,
            "source_row_count": len(payload.source_rows),
            "draft_rows": [],
            "row_warnings": [],
            "blocking_errors": [_issue_to_import_issue(error) for error in validation_report["blocking_errors"]],
            "mapping_validation": validation_report,
            "governance_note": GOVERNANCE_NOTE,
        }

    role_to_source = {
        mapping["target_role"]: mapping["source_column"]
        for mapping in validation_report["accepted_mappings"]
    }

    draft_rows = []
    row_warnings = []

    for index, source_row in enumerate(payload.source_rows, start=1):
        draft_row, warnings = _transform_row(index, source_row, role_to_source)
        draft_rows.append(draft_row)
        row_warnings.extend(warnings)

    return {
        "import_status": "ready_with_warnings" if row_warnings or validation_report["warnings"] else "ready",
        "draft_row_count": len(draft_rows),
        "source_row_count": len(payload.source_rows),
        "draft_rows": draft_rows,
        "row_warnings": row_warnings,
        "blocking_errors": [],
        "mapping_validation": validation_report,
        "governance_note": GOVERNANCE_NOTE,
    }


def _blocked_report(payload, validation_report: dict, blocking_error: dict) -> dict:
    return {
        "import_status": "blocked",
        "draft_row_count": 0,
        "source_row_count": len(payload.source_rows),
        "draft_rows": [],
        "row_warnings": [],
        "blocking_errors": [blocking_error],
        "mapping_validation": validation_report,
        "governance_note": GOVERNANCE_NOTE,
    }


def _transform_row(row_number: int, source_row: dict, role_to_source: dict[str, str]) -> tuple[dict, list[dict]]:
    warnings: list[dict] = []

    def value_for(role: str, default: object = ""):
        source_column = role_to_source.get(role)
        if not source_column:
            return default
        return source_row.get(source_column, default)

    stream_id = _clean_text(value_for("stream_id"))
    if not stream_id:
        stream_id = f"DRAFT-{row_number:04d}"
        warnings.append(
            _warning(
                row_number,
                "generated_stream_id",
                None,
                "stream_id",
                "No confirmed Stream ID column was available, so a draft ID was generated.",
            )
        )

    material = _required_text(row_number, value_for("material"), "material", warnings)
    current_route = _required_text(row_number, value_for("current_route"), "current_route", warnings)
    quantity_value = value_for("quantity")
    quantity_unit = _clean_text(value_for("quantity_unit", "kg")) or "kg"
    monthly_quantity_kg = _quantity_to_kg(row_number, quantity_value, quantity_unit, warnings)

    disposal_cost_per_month = _optional_float(
        row_number,
        value_for("disposal_cost_per_month", 0),
        "disposal_cost_per_month",
        warnings,
    )

    stream_name = _clean_text(value_for("stream_name")) or material or stream_id
    source_process = _clean_text(value_for("source_process")) or UNKNOWN
    contamination_risk = _clean_text(value_for("contamination_risk")) or UNKNOWN
    hazardous_flag = _clean_text(value_for("hazardous_flag")) or UNKNOWN
    department = _clean_text(value_for("department")) or UNKNOWN
    supplier = _clean_text(value_for("supplier")) or UNKNOWN
    supplier_takeback_available = _clean_text(value_for("supplier_takeback_available")) or UNKNOWN
    recycled_content_available = _clean_text(value_for("recycled_content_available")) or UNKNOWN
    notes = _clean_text(value_for("notes"))

    return {
        "source_row_number": row_number,
        "stream_id": stream_id,
        "stream_name": stream_name,
        "material": material,
        "source_process": source_process,
        "monthly_quantity_kg": monthly_quantity_kg,
        "current_route": current_route,
        "disposal_cost_per_month": disposal_cost_per_month,
        "contamination_risk": contamination_risk,
        "hazardous_flag": hazardous_flag,
        "department": department,
        "supplier": supplier,
        "supplier_takeback_available": supplier_takeback_available,
        "recycled_content_available": recycled_content_available,
        "notes": notes,
        "draft_status": "draft_only_not_imported",
        "claim_boundary": "Draft transformed row only. Not verified operational data and not a savings, diversion or compliance claim.",
    }, warnings


def _clean_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() in {"", "nan", "none", "null"}:
        return ""
    return text


def _required_text(row_number: int, value: object, role: str, warnings: list[dict]) -> str:
    cleaned = _clean_text(value)
    if cleaned:
        return cleaned
    warnings.append(
        _warning(
            row_number,
            "missing_required_value",
            None,
            role,
            f"Required role '{role}' was mapped but this row has an empty value.",
        )
    )
    return UNKNOWN


def _optional_float(row_number: int, value: object, role: str, warnings: list[dict]) -> float:
    cleaned = _clean_text(value)
    if not cleaned:
        return 0.0
    try:
        return float(str(cleaned).replace(",", "").replace("£", "").strip())
    except ValueError:
        warnings.append(
            _warning(
                row_number,
                "invalid_numeric_value",
                None,
                role,
                f"Optional numeric role '{role}' could not be parsed and was set to 0.",
            )
        )
        return 0.0


def _quantity_to_kg(row_number: int, value: object, unit: str, warnings: list[dict]) -> float:
    cleaned = _clean_text(value)
    if not cleaned:
        warnings.append(
            _warning(
                row_number,
                "missing_required_value",
                None,
                "quantity",
                "Required quantity value is empty and was set to 0 kg for draft review.",
            )
        )
        return 0.0

    try:
        numeric = float(str(cleaned).replace(",", "").strip())
    except ValueError:
        warnings.append(
            _warning(
                row_number,
                "invalid_quantity",
                None,
                "quantity",
                "Quantity could not be parsed and was set to 0 kg for draft review.",
            )
        )
        return 0.0

    normalised_unit = unit.strip().lower()
    if normalised_unit in {"kg", "kilogram", "kilograms", "kgs"}:
        return numeric
    if normalised_unit in {"t", "tonne", "tonnes", "metric tonne", "metric tonnes"}:
        return numeric * 1000
    if normalised_unit in {"g", "gram", "grams"}:
        return numeric / 1000

    warnings.append(
        _warning(
            row_number,
            "unknown_quantity_unit",
            None,
            "quantity_unit",
            f"Quantity unit '{unit}' is not recognised; value was treated as kilograms for draft review.",
        )
    )
    return numeric


def _warning(row_number: int, code: str, source_column: str | None, target_role: str | None, message: str) -> dict:
    return {
        "code": code,
        "message": message,
        "source_row_number": row_number,
        "source_column": source_column,
        "target_role": target_role,
    }


def _issue_to_import_issue(issue: dict) -> dict:
    return {
        "code": issue.get("code", "mapping_validation_blocker"),
        "message": issue.get("message", "Mapping validation blocked flexible import."),
        "source_row_number": None,
        "source_column": issue.get("source_column"),
        "target_role": issue.get("target_role"),
    }
