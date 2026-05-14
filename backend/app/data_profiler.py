"""Milestone 14A backend data profiler and column alias mapper."""

from __future__ import annotations

from io import BytesIO

import pandas as pd

from app.data_profiler_config import (
    GOVERNANCE_NOTE,
    ROLE_ALIASES,
    ROLE_LABELS,
    VALUE_HINTS,
    WORKSPACE_RULES,
)
from app.data_profiler_role_scoring import normalise, role_candidates
from app.data_profiler_type_inference import infer_type, sample_values


def _column_profile(name: str, series: pd.Series) -> dict:
    candidates = role_candidates(name, series)
    top = candidates[0] if candidates else None
    second = candidates[1] if len(candidates) > 1 else None
    gap = (top["confidence"] - second["confidence"]) if top and second else 100
    missing = int(series.isna().sum())
    total = len(series)

    return {
        "original_name": str(name),
        "normalised_name": normalise(name),
        "inferred_data_type": infer_type(series),
        "missing_count": missing,
        "missing_percentage": round((missing / total) * 100, 2) if total else 0.0,
        "unique_count": int(series.nunique(dropna=True)),
        "sample_values": sample_values(series),
        "mapped_role": top["role"] if top else None,
        "mapped_role_label": top["label"] if top else None,
        "role_confidence": top["confidence"] if top else 0,
        "role_reason": top["reason"] if top else "No confident alias or value-pattern match.",
        "confirmation_required": bool(top and (top["confidence"] < 85 or gap < 12)),
        "alternatives": candidates[1:],
    }


def _role_mapping(columns: list[dict]) -> dict[str, dict]:
    mapping = {}
    for column in sorted(columns, key=lambda item: item["role_confidence"], reverse=True):
        role = column.get("mapped_role")
        if role and role not in mapping:
            mapping[role] = column
    return mapping


def _workspace_score(rule: dict, mapped_roles: set[str]) -> int:
    required = rule.get("required", [])
    important = rule.get("important", [])
    if not required:
        return 20
    required_hits = sum(1 for role in required if role in mapped_roles)
    important_hits = sum(1 for role in important if role in mapped_roles)
    return int(round((required_hits / len(required)) * 70 + (important_hits / max(len(important), 1)) * 30))


def _status(score: int) -> str:
    if score >= 80:
        return "strong match"
    if score >= 55:
        return "partial match"
    if score >= 30:
        return "weak match"
    return "not enough mapped data"


def _workspace_rows(mapped_roles: set[str]) -> list[dict]:
    rows = []
    for workspace_id, rule in WORKSPACE_RULES.items():
        score = 100 if workspace_id == "data-profiler" else _workspace_score(rule, mapped_roles)
        roles = rule.get("required", []) + rule.get("important", [])
        rows.append({
            "workspace_id": workspace_id,
            "label": rule["label"],
            "score": score,
            "status": "available profiler route" if workspace_id == "data-profiler" else _status(score),
            "matched_roles": [{"role": role, "label": ROLE_LABELS.get(role, role)} for role in roles if role in mapped_roles],
            "missing_roles": [{"role": role, "label": ROLE_LABELS.get(role, role)} for role in roles if role not in mapped_roles],
            "available_analysis": rule["available"],
            "unavailable_analysis": rule["unavailable"],
            "governance_boundary": GOVERNANCE_NOTE,
        })
    return sorted(rows, key=lambda row: row["score"], reverse=True)


def _summary(best: dict, mapped_roles: set[str]) -> tuple[list[str], list[str], str]:
    available = list(best["available_analysis"])
    unavailable = list(best["unavailable_analysis"])
    if "quantity" not in mapped_roles:
        unavailable.append("quantity-based screening until a quantity/weight column is mapped")
    if best["workspace_id"] == "circular-core":
        if "hazardous_flag" not in mapped_roles:
            unavailable.append("hazardous review is limited until hazardous status is provided")
        if "contamination_risk" not in mapped_roles:
            unavailable.append("contamination-sensitive recommendations are limited until contamination risk is provided")
        if "disposal_cost_per_month" not in mapped_roles:
            unavailable.append("cost exposure screening is unavailable until cost data is mapped")
    return available, unavailable, "Review the mapped columns and confirm uncertain roles before flexible import or domain analysis."


def profile_csv_bytes(file_bytes: bytes, dataset_label: str = "uploaded dataset") -> dict:
    if not file_bytes:
        raise ValueError("Uploaded CSV file is empty.")
    try:
        df = pd.read_csv(BytesIO(file_bytes), encoding="utf-8-sig")
    except Exception as exc:
        raise ValueError(f"Could not parse uploaded CSV: {exc}") from exc
    if len(df.columns) == 0:
        raise ValueError("Uploaded CSV does not contain columns.")

    columns = [_column_profile(column, df[column]) for column in df.columns]
    mapping = _role_mapping(columns)
    mapped_roles = set(mapping)
    workspace_rows = _workspace_rows(mapped_roles)
    non_profiler = [row for row in workspace_rows if row["workspace_id"] != "data-profiler"]
    best = next((row for row in non_profiler if row["score"] >= 30), workspace_rows[0])
    available, unavailable, next_action = _summary(best, mapped_roles)

    return {
        "dataset_label": dataset_label,
        "total_rows": int(len(df)),
        "total_columns": int(len(df.columns)),
        "duplicate_rows": int(df.duplicated().sum()),
        "detected_workspace": best["workspace_id"],
        "detected_workspace_label": best["label"],
        "workspace_confidence": int(best["score"]),
        "workspace_status": best["status"],
        "columns": columns,
        "role_mapping": [
            {
                "role": role,
                "label": ROLE_LABELS.get(role, role),
                "source_column": column["original_name"],
                "confidence": column["role_confidence"],
                "confirmation_required": column["confirmation_required"],
            }
            for role, column in mapping.items()
        ],
        "workspace_compatibility": workspace_rows,
        "available_analysis_routes": available,
        "unavailable_analysis_routes": unavailable,
        "recommended_next_action": next_action,
        "governance_note": GOVERNANCE_NOTE,
    }
