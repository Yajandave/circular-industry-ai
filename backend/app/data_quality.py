"""Data quality profiling for industrial stream datasets."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app import schemas


_ALLOWED_RISK_VALUES = {"low", "medium", "high", "unknown"}
_ALLOWED_TRI_STATE = {"yes", "no", "unknown", "true", "false"}


def _value(record: Any, field: str) -> Any:
    if isinstance(record, dict):
        return record.get(field)
    return getattr(record, field, None)


def _text(record: Any, field: str) -> str:
    value = _value(record, field)
    if value is None:
        return ""
    return str(value).strip()


def _number(record: Any, field: str) -> float:
    try:
        return float(_value(record, field) or 0)
    except Exception:
        return 0.0


def _issue(
    *,
    issue_type: str,
    severity: str,
    field: str,
    stream_id: str | None,
    message: str,
    recommended_action: str,
) -> schemas.DataQualityIssue:
    return schemas.DataQualityIssue(
        issue_type=issue_type,
        severity=severity,
        field=field,
        stream_id=stream_id,
        message=message,
        recommended_action=recommended_action,
    )


def build_data_quality_report(records: list[Any], *, dataset_label: str = "current dataset") -> schemas.DataQualityReport:
    """Build a deterministic data-quality profile for stream-like records."""
    issues: list[schemas.DataQualityIssue] = []
    total = len(records)

    stream_ids = [_text(record, "stream_id") for record in records]
    duplicate_ids = sorted([stream_id for stream_id, count in Counter(stream_ids).items() if stream_id and count > 1])

    for duplicate_id in duplicate_ids:
        issues.append(
            _issue(
                issue_type="duplicate_stream_id",
                severity="critical",
                field="stream_id",
                stream_id=duplicate_id,
                message=f"Duplicate stream ID found: {duplicate_id}.",
                recommended_action="Stream IDs must be unique before analysis outputs are trusted.",
            )
        )

    required_text_fields = [
        "stream_id",
        "stream_name",
        "material",
        "source_process",
        "current_route",
        "contamination_risk",
        "hazardous_flag",
        "department",
        "supplier",
        "supplier_takeback_available",
        "recycled_content_available",
    ]

    for record in records:
        stream_id = _text(record, "stream_id") or "unknown"
        for field in required_text_fields:
            if not _text(record, field):
                issues.append(
                    _issue(
                        issue_type="missing_required_value",
                        severity="critical",
                        field=field,
                        stream_id=stream_id,
                        message=f"{field} is blank for stream {stream_id}.",
                        recommended_action="Fill the required value before running decision-support outputs.",
                    )
                )

        quantity = _number(record, "monthly_quantity_kg")
        cost = _number(record, "disposal_cost_per_month")
        contamination = _text(record, "contamination_risk").lower()
        hazardous = _text(record, "hazardous_flag").lower()
        takeback = _text(record, "supplier_takeback_available").lower()
        recycled = _text(record, "recycled_content_available").lower()
        supplier = _text(record, "supplier").lower()

        if quantity <= 0:
            issues.append(
                _issue(
                    issue_type="invalid_quantity",
                    severity="critical",
                    field="monthly_quantity_kg",
                    stream_id=stream_id,
                    message=f"Monthly quantity must be positive for stream {stream_id}.",
                    recommended_action="Replace zero/negative quantities with measured or estimated values and mark assumptions in notes.",
                )
            )

        if cost < 0:
            issues.append(
                _issue(
                    issue_type="invalid_cost",
                    severity="critical",
                    field="disposal_cost_per_month",
                    stream_id=stream_id,
                    message=f"Disposal cost cannot be negative for stream {stream_id}.",
                    recommended_action="Check finance/source records and correct the disposal cost.",
                )
            )

        if contamination and contamination not in _ALLOWED_RISK_VALUES:
            issues.append(
                _issue(
                    issue_type="unexpected_category",
                    severity="warning",
                    field="contamination_risk",
                    stream_id=stream_id,
                    message=f"Unexpected contamination_risk value '{contamination}' for stream {stream_id}.",
                    recommended_action="Use low, medium, high or unknown so rules and dashboards remain consistent.",
                )
            )

        if hazardous == "unknown":
            issues.append(
                _issue(
                    issue_type="unknown_hazard_status",
                    severity="warning",
                    field="hazardous_flag",
                    stream_id=stream_id,
                    message=f"Hazard status is unknown for stream {stream_id}.",
                    recommended_action="Confirm hazardous classification before circular routing or supplier claims.",
                )
            )

        if contamination == "high":
            issues.append(
                _issue(
                    issue_type="high_contamination",
                    severity="warning",
                    field="contamination_risk",
                    stream_id=stream_id,
                    message=f"High contamination risk recorded for stream {stream_id}.",
                    recommended_action="Collect contamination assessment evidence before selecting a circular route.",
                )
            )

        if takeback and takeback not in _ALLOWED_TRI_STATE:
            issues.append(
                _issue(
                    issue_type="unexpected_category",
                    severity="warning",
                    field="supplier_takeback_available",
                    stream_id=stream_id,
                    message=f"Unexpected supplier_takeback_available value '{takeback}' for stream {stream_id}.",
                    recommended_action="Use yes, no or unknown for supplier take-back availability.",
                )
            )

        if recycled and recycled not in _ALLOWED_TRI_STATE:
            issues.append(
                _issue(
                    issue_type="unexpected_category",
                    severity="warning",
                    field="recycled_content_available",
                    stream_id=stream_id,
                    message=f"Unexpected recycled_content_available value '{recycled}' for stream {stream_id}.",
                    recommended_action="Use yes, no or unknown for recycled-content availability.",
                )
            )

        if supplier in {"various", "various suppliers", "unknown", "n/a", "na"}:
            issues.append(
                _issue(
                    issue_type="weak_supplier_specificity",
                    severity="info",
                    field="supplier",
                    stream_id=stream_id,
                    message=f"Supplier field is not specific for stream {stream_id}.",
                    recommended_action="Split the stream by supplier or document the responsible supplier group before procurement action.",
                )
            )

    critical_count = sum(1 for issue in issues if issue.severity == "critical")
    warning_count = sum(1 for issue in issues if issue.severity == "warning")
    info_count = sum(1 for issue in issues if issue.severity == "info")

    score = 100
    score -= critical_count * 12
    score -= warning_count * 4
    score -= info_count * 1
    readiness_score = max(0, min(100, score))

    if critical_count:
        readiness_status = "blocked: critical data issues"
    elif warning_count >= 15:
        readiness_status = "review required: many warnings"
    elif warning_count:
        readiness_status = "usable with review"
    else:
        readiness_status = "ready for rules screening"

    top_quantity_streams = sorted(
        [
            {
                "stream_id": _text(record, "stream_id"),
                "stream_name": _text(record, "stream_name"),
                "monthly_quantity_kg": _number(record, "monthly_quantity_kg"),
            }
            for record in records
        ],
        key=lambda item: item["monthly_quantity_kg"],
        reverse=True,
    )[:5]

    top_cost_streams = sorted(
        [
            {
                "stream_id": _text(record, "stream_id"),
                "stream_name": _text(record, "stream_name"),
                "disposal_cost_per_month": _number(record, "disposal_cost_per_month"),
            }
            for record in records
        ],
        key=lambda item: item["disposal_cost_per_month"],
        reverse=True,
    )[:5]

    return schemas.DataQualityReport(
        dataset_label=dataset_label,
        total_records=total,
        readiness_status=readiness_status,
        readiness_score=readiness_score,
        critical_issue_count=critical_count,
        warning_issue_count=warning_count,
        info_issue_count=info_count,
        duplicate_stream_ids=duplicate_ids,
        material_breakdown=dict(Counter(_text(record, "material") or "unknown" for record in records)),
        department_breakdown=dict(Counter(_text(record, "department") or "unknown" for record in records)),
        high_risk_data_flags={
            "unknown_hazard_status": sum(1 for record in records if _text(record, "hazardous_flag").lower() == "unknown"),
            "high_contamination": sum(1 for record in records if _text(record, "contamination_risk").lower() == "high"),
            "non_specific_supplier": sum(1 for record in records if _text(record, "supplier").lower() in {"various", "various suppliers", "unknown", "n/a", "na"}),
        },
        top_quantity_streams=top_quantity_streams,
        top_cost_streams=top_cost_streams,
        issues=issues[:150],
        governance_note=(
            "Data-quality reports support screening readiness. They do not verify legal waste classification, "
            "supplier capability, environmental benefit, carbon impact or financial savings."
        ),
    )
