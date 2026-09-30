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

KG_UNITS = {"kg", "kilogram", "kilograms", "kgs"}
TONNE_UNITS = {"t", "tonne", "tonnes", "metric tonne", "metric tonnes"}
GRAM_UNITS = {"g", "gram", "grams"}
SUPPORTED_MASS_UNITS = KG_UNITS | TONNE_UNITS | GRAM_UNITS


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

    unit_blockers = _quantity_unit_blockers(payload.source_rows, role_to_source)
    if unit_blockers:
        return {
            "import_status": "blocked",
            "draft_row_count": 0,
            "source_row_count": len(payload.source_rows),
            "draft_rows": [],
            "row_warnings": [],
            "blocking_errors": unit_blockers,
            "mapping_validation": validation_report,
            "governance_note": GOVERNANCE_NOTE,
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
    quantity_unit = _clean_text(value_for("quantity_unit"))
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
    source_provenance = _build_source_provenance(
        row_number=row_number,
        source_row=source_row,
        role_to_source=role_to_source,
        stream_id=stream_id,
        stream_name=stream_name,
        material=material,
        source_process=source_process,
        monthly_quantity_kg=monthly_quantity_kg,
        quantity_unit=quantity_unit,
        current_route=current_route,
        disposal_cost_per_month=disposal_cost_per_month,
        contamination_risk=contamination_risk,
        hazardous_flag=hazardous_flag,
        department=department,
        supplier=supplier,
        supplier_takeback_available=supplier_takeback_available,
        recycled_content_available=recycled_content_available,
        notes=notes,
    )

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
        "source_provenance": source_provenance,
        "draft_status": "draft_only_not_imported",
        "claim_boundary": "Draft transformed row only. Not verified operational data and not a savings, diversion or compliance claim.",
    }, warnings


def _build_source_provenance(
    *,
    row_number: int,
    source_row: dict,
    role_to_source: dict[str, str],
    stream_id: str,
    stream_name: str,
    material: str,
    source_process: str,
    monthly_quantity_kg: float,
    quantity_unit: str,
    current_route: str,
    disposal_cost_per_month: float,
    contamination_risk: str,
    hazardous_flag: str,
    department: str,
    supplier: str,
    supplier_takeback_available: str,
    recycled_content_available: str,
    notes: str,
) -> list[dict]:
    """Capture field-level source lineage for the draft transformation."""

    def raw(role: str) -> tuple[str | None, str]:
        source_column = role_to_source.get(role)
        if not source_column:
            return None, ""
        return source_column, _clean_text(source_row.get(source_column))

    def text_entry(target_field: str, role: str, transformed: str, fallback: str) -> dict:
        source_column, source_value = raw(role)
        transformation = "trim_text" if source_value else fallback
        return {
            "target_field": target_field,
            "source_column": source_column,
            "source_value": source_value,
            "source_unit": None,
            "transformed_value": str(transformed),
            "transformation": transformation,
        }

    provenance: list[dict] = []

    stream_id_column, stream_id_value = raw("stream_id")
    provenance.append({
        "target_field": "stream_id",
        "source_column": stream_id_column,
        "source_value": stream_id_value,
        "source_unit": None,
        "transformed_value": str(stream_id),
        "transformation": "trim_text" if stream_id_value else f"generated_draft_id_from_source_row_{row_number}",
    })

    stream_name_column, stream_name_value = raw("stream_name")
    provenance.append({
        "target_field": "stream_name",
        "source_column": stream_name_column,
        "source_value": stream_name_value,
        "source_unit": None,
        "transformed_value": str(stream_name),
        "transformation": "trim_text" if stream_name_value else "fallback_from_material_or_stream_id",
    })

    provenance.append(text_entry("material", "material", material, "default_unknown"))
    provenance.append(text_entry("source_process", "source_process", source_process, "default_unknown"))

    quantity_column, quantity_value = raw("quantity")
    normalised_unit = quantity_unit.strip().lower()
    quantity_transformation = (
        "kg_identity"
        if normalised_unit in KG_UNITS
        else "tonnes_to_kg"
        if normalised_unit in TONNE_UNITS
        else "grams_to_kg"
        if normalised_unit in GRAM_UNITS
        else "unsupported_unit_blocked"
    )
    provenance.append({
        "target_field": "monthly_quantity_kg",
        "source_column": quantity_column,
        "source_value": quantity_value,
        "source_unit": quantity_unit or None,
        "transformed_value": str(monthly_quantity_kg),
        "transformation": quantity_transformation,
    })

    provenance.append(text_entry("current_route", "current_route", current_route, "default_unknown"))

    cost_column, cost_value = raw("disposal_cost_per_month")
    if not cost_value:
        cost_transformation = "default_zero"
    else:
        try:
            float(cost_value.replace(",", "").replace("£", "").strip())
            cost_transformation = "numeric_parse"
        except ValueError:
            cost_transformation = "numeric_parse_failed_to_zero"
    provenance.append({
        "target_field": "disposal_cost_per_month",
        "source_column": cost_column,
        "source_value": cost_value,
        "source_unit": None,
        "transformed_value": str(disposal_cost_per_month),
        "transformation": cost_transformation,
    })

    provenance.extend([
        text_entry("contamination_risk", "contamination_risk", contamination_risk, "default_unknown"),
        text_entry("hazardous_flag", "hazardous_flag", hazardous_flag, "default_unknown"),
        text_entry("department", "department", department, "default_unknown"),
        text_entry("supplier", "supplier", supplier, "default_unknown"),
        text_entry(
            "supplier_takeback_available",
            "supplier_takeback_available",
            supplier_takeback_available,
            "default_unknown",
        ),
        text_entry(
            "recycled_content_available",
            "recycled_content_available",
            recycled_content_available,
            "default_unknown",
        ),
        text_entry("notes", "notes", notes, "default_empty"),
    ])

    return provenance


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


def _quantity_unit_blockers(source_rows: list[dict], role_to_source: dict[str, str]) -> list[dict]:
    """Block kg-based quantitative import when the mass unit is not explicit and supported."""
    source_column = role_to_source.get("quantity_unit")
    if not source_column:
        return [
            {
                "code": "missing_quantity_unit_mapping",
                "message": (
                    "Quantity is mapped but no quantity-unit column has been confirmed. "
                    "Circular Core will not assume kilograms; map an explicit kg, g or tonne unit before quantitative import."
                ),
                "source_row_number": None,
                "source_column": None,
                "target_role": "quantity_unit",
            }
        ]

    blockers: list[dict] = []
    for row_number, source_row in enumerate(source_rows, start=1):
        raw_unit = _clean_text(source_row.get(source_column))
        normalised_unit = raw_unit.lower()

        if not raw_unit:
            blockers.append(
                {
                    "code": "missing_quantity_unit",
                    "message": (
                        "Quantity unit is empty. Confirm a supported mass unit (kg, g or tonne) "
                        "before quantitative Circular Core analysis."
                    ),
                    "source_row_number": row_number,
                    "source_column": source_column,
                    "target_role": "quantity_unit",
                }
            )
            continue

        if normalised_unit not in SUPPORTED_MASS_UNITS:
            blockers.append(
                {
                    "code": "unsupported_quantity_unit",
                    "message": (
                        f"Quantity unit '{raw_unit}' is not supported by the current kg-based import. "
                        "Convert or confirm the value in kg, g or tonnes before quantitative Circular Core analysis."
                    ),
                    "source_row_number": row_number,
                    "source_column": source_column,
                    "target_role": "quantity_unit",
                }
            )

    return blockers


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
    if normalised_unit in KG_UNITS:
        return numeric
    if normalised_unit in TONNE_UNITS:
        return numeric * 1000
    if normalised_unit in GRAM_UNITS:
        return numeric / 1000

    # Defensive fallback. Normal workflow is blocked earlier by
    # _quantity_unit_blockers, but never reinterpret an unsupported unit as kg.
    warnings.append(
        _warning(
            row_number,
            "unsupported_quantity_unit",
            None,
            "quantity_unit",
            f"Quantity unit '{unit}' is unsupported; quantitative mass value was set to 0 for safe draft handling.",
        )
    )
    return 0.0


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
