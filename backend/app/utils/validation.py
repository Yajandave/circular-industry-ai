"""Validation helpers for industrial stream CSV files."""

from __future__ import annotations

import math

import pandas as pd

from app.utils.upload_security import MAX_CSV_COLUMNS, MAX_CSV_ROWS

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
    if len(df.columns) > MAX_CSV_COLUMNS:
        raise ValueError(f"CSV contains more than the {MAX_CSV_COLUMNS}-column limit.")
    if len(df) > MAX_CSV_ROWS:
        raise ValueError(f"CSV contains more than the {MAX_CSV_ROWS}-row limit.")
    if len(df) == 0:
        raise ValueError("CSV must contain at least one data row.")
    if not df.columns.is_unique:
        raise ValueError("CSV contains duplicate column names.")

    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"CSV is missing required columns: {missing_text}")

    required_values = [column for column in REQUIRED_COLUMNS if column != "notes"]
    blank_cells: list[str] = []
    for column in required_values:
        blank_mask = df[column].isna() | df[column].astype(str).str.strip().eq("")
        if blank_mask.any():
            rows = ", ".join(str(index + 2) for index in df.index[blank_mask][:5])
            blank_cells.append(f"{column} (CSV row {rows})")
    if blank_cells:
        raise ValueError("CSV contains missing required values: " + "; ".join(blank_cells))

    stream_ids = df["stream_id"].astype(str).str.strip()
    duplicate_ids = sorted(stream_ids[stream_ids.duplicated(keep=False)].unique())
    if duplicate_ids:
        raise ValueError(f"CSV contains duplicate stream_id values: {', '.join(duplicate_ids[:10])}")

    for column in ("monthly_quantity_kg", "disposal_cost_per_month"):
        numeric = pd.to_numeric(df[column], errors="coerce")
        invalid_mask = numeric.isna() | ~numeric.map(math.isfinite) | numeric.lt(0)
        if invalid_mask.any():
            rows = ", ".join(str(index + 2) for index in df.index[invalid_mask][:5])
            raise ValueError(
                f"Column '{column}' must contain finite, non-negative numbers (CSV row {rows})."
            )


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
