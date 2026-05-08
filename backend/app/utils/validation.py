"""Validation helpers for industrial stream CSV files."""

from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = [
    "stream_id",
    "stream_name",
    "material",
    "source_process",
    "monthly_quantity_kg",
    "current_route",
    "disposal_cost_per_month",
    "contamination_risk",
    "hazardous_flag",
    "department",
    "supplier",
    "supplier_takeback_available",
    "recycled_content_available",
    "notes",
]


def validate_required_columns(df: pd.DataFrame) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"CSV is missing required columns: {missing_text}")


def normalise_hazardous_flag(value: object) -> str:
    """Normalise hazardous flag values while preserving unknown status for review."""
    if isinstance(value, bool):
        return "true" if value else "false"
    text = str(value).strip().lower()
    if text in {"true", "yes", "1", "y"}:
        return "true"
    if text in {"false", "no", "0", "n"}:
        return "false"
    if text in {"unknown", "unclear", "not known", "n/a", "na", ""}:
        return "unknown"
    raise ValueError(f"Cannot normalise hazardous_flag value: {value}")
