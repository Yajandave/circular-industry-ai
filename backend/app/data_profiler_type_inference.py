"""Type inference helpers for the Data Profiler.

This module keeps sample extraction and deterministic type detection separate
from role mapping, workspace routing and CSV profiling orchestration.
"""

from __future__ import annotations

from datetime import datetime
import re

import pandas as pd


_DATE_FORMATS = (
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%d.%m.%Y",
    "%d/%m/%y",
    "%d-%m-%y",
    "%m/%d/%Y",
    "%m-%d-%Y",
)
_DATE_LIKE_PATTERN = re.compile(
    r"^(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})$"
)


def sample_values(series: pd.Series, limit: int = 6) -> list[str]:
    """Return a small set of non-empty unique sample values for UI review."""

    values = []
    for value in series.dropna().astype(str).head(40).tolist():
        cleaned = value.strip()
        if cleaned and cleaned.lower() not in {"nan", "none", "null"} and cleaned not in values:
            values.append(cleaned)
        if len(values) >= limit:
            break
    return values


def infer_type(series: pd.Series) -> str:
    """Infer a coarse profiler data type without unsafe date parsing warnings."""

    non_null = series.dropna()
    if non_null.empty:
        return "empty"

    numeric = pd.to_numeric(non_null, errors="coerce")
    if numeric.notna().mean() >= 0.85:
        return "numeric"

    if _date_parse_success_ratio(non_null) >= 0.75:
        return "date"

    unique_ratio = non_null.astype(str).nunique(dropna=True) / max(len(non_null), 1)
    return "categorical" if unique_ratio <= 0.35 else "text"


def _date_parse_success_ratio(non_null: pd.Series) -> float:
    """Return deterministic date-like parse ratio without pandas format inference warnings.

    The profiler only needs a safe column-type signal here. It should not infer,
    normalise or verify actual reporting periods at this stage.
    """

    values = [
        str(value).strip()
        for value in non_null.tolist()
        if str(value).strip().lower() not in {"", "nan", "none", "null"}
    ]
    if not values:
        return 0.0

    date_like_values = [value for value in values if _DATE_LIKE_PATTERN.match(value)]
    if len(date_like_values) / len(values) < 0.75:
        return 0.0

    parsed_count = 0
    for value in date_like_values:
        if any(_matches_date_format(value, date_format) for date_format in _DATE_FORMATS):
            parsed_count += 1

    return parsed_count / len(values)


def _matches_date_format(value: str, date_format: str) -> bool:
    try:
        datetime.strptime(value, date_format)
    except ValueError:
        return False
    return True
