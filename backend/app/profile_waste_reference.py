"""Enrich an existing CSV profile with optional local waste-code reference matches.

This does not modify the Data Profiler's existing contract or imply legal classification.
"""
from __future__ import annotations

from io import BytesIO
import pandas as pd

from app.data_profiler import profile_csv_bytes
from app.wdi_reference_lookup import lookup_reported_waste_code
from app.reference_decision_eligibility import evaluate_reference_decision_eligibility

WASTE_CODE_HEADERS = {"waste code", "ewc code", "e wc code", "european waste code", "list of waste code", "low code"}

def profile_with_waste_reference(file_bytes: bytes, filename: str) -> dict:
    profile = profile_csv_bytes(file_bytes, dataset_label=filename)
    data = pd.read_csv(BytesIO(file_bytes), encoding="utf-8-sig", dtype=str)
    candidate_columns = [
        col for col in data.columns
        if " ".join(str(col).lower().replace("_", " ").replace("-", " ").split()) in WASTE_CODE_HEADERS
    ]
    if len(candidate_columns) != 1:
        return {
            "profile": profile,
            "reference_status": "no_unambiguous_waste_code_column",
            "waste_code_column": None,
            "waste_code_lookups": [],
            "note": "Normal Data Profiler output retained. No verified waste-code column was established.",
        }
    column = candidate_columns[0]
    codes = list(dict.fromkeys(str(value).strip() for value in data[column].dropna() if str(value).strip()))
    if len(codes) > 1000:
        return {
            "profile": profile,
            "reference_status": "too_many_distinct_codes",
            "waste_code_column": column,
            "waste_code_lookups": [],
            "note": "Reference enrichment is capped at 1000 distinct codes per request; original profile remains available.",
        }
    lookups = []
    for code in codes:
        lookup = lookup_reported_waste_code(code)
        lookup['decision_eligibility'] = evaluate_reference_decision_eligibility(lookup)
        lookups.append(lookup)
    return {
        "profile": profile,
        "reference_status": "evaluated",
        "waste_code_column": column,
        "waste_code_lookups": lookups,
        "note": "Reported source reference matches are lookup-only and cannot change rules, hazard flags, material grades or recommendations.",
    }
