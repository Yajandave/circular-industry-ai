"""Safety helpers for spreadsheet-compatible CSV exports."""

from __future__ import annotations

from collections.abc import Iterable


DANGEROUS_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r", "\n")


def protect_csv_value(value: object) -> object:
    """Prevent user-controlled text from being interpreted as a spreadsheet formula."""
    if not isinstance(value, str):
        return value
    if value.lstrip().startswith(DANGEROUS_FORMULA_PREFIXES):
        return "'" + value
    return value


def protect_csv_rows(rows: Iterable[dict]) -> list[dict]:
    return [
        {key: protect_csv_value(value) for key, value in row.items()}
        for row in rows
    ]
