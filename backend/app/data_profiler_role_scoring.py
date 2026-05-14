"""Semantic role-scoring helpers for the Data Profiler.

This module keeps header normalisation, token scoring, value-hint scoring and
candidate generation separate from CSV profiling orchestration.
"""

from __future__ import annotations

import re

import pandas as pd

from app.data_profiler_config import ROLE_ALIASES, ROLE_LABELS, VALUE_HINTS
from app.data_profiler_type_inference import infer_type, sample_values


def normalise(value: object) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[_\-/]+", " ", text)
    text = re.sub(r"[^a-z0-9£% ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokens(value: object) -> set[str]:
    return {token for token in normalise(value).split(" ") if token}


def role_candidates(header: str, series: pd.Series) -> list[dict]:
    normalised = normalise(header)
    header_tokens = tokens(header)
    samples = sample_values(series)
    inferred_type = infer_type(series)
    candidates = []

    for role, aliases in ROLE_ALIASES.items():
        best_score = 0
        best_reason = ""
        for alias in aliases:
            alias_norm = normalise(alias)
            alias_tokens = tokens(alias)
            if normalised == alias_norm:
                score = 86
                reason = f"header matches alias '{alias}'"
            elif alias_norm and alias_norm in normalised:
                score = 74
                reason = f"header contains alias '{alias}'"
            else:
                score = int((len(header_tokens & alias_tokens) / max(len(alias_tokens), 1)) * 58)
                reason = f"header token overlap with alias '{alias}'"
            score += _value_score(role, samples)
            score += _type_score(role, inferred_type, normalised)
            if score > best_score:
                best_score = score
                best_reason = reason
        if best_score >= 35:
            candidates.append(
                {
                    "role": role,
                    "label": ROLE_LABELS.get(role, role),
                    "confidence": min(best_score, 99),
                    "reason": best_reason,
                }
            )

    return sorted(candidates, key=lambda item: item["confidence"], reverse=True)[:4]


def _value_score(role: str, samples: list[str]) -> int:
    joined = " ".join(samples).lower()
    return min(18, sum(1 for hint in VALUE_HINTS.get(role, []) if hint in joined) * 6)


def _type_score(role: str, inferred_type: str, header: str) -> int:
    numeric_roles = {"quantity", "disposal_cost_per_month", "spend", "emissions_quantity", "emission_factor", "esg_score"}
    year_roles = {"reporting_year", "baseline_year", "target_year"}
    if role in numeric_roles and inferred_type == "numeric":
        return 10
    if role in year_roles and inferred_type in {"date", "numeric"}:
        return 8
    if role == "disposal_cost_per_month" and ("£" in header or "cost" in header or "spend" in header):
        return 8
    return 0
