"""Risk, evidence and confidence scoring for circular economy recommendations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class StreamLike(Protocol):
    stream_id: str
    stream_name: str
    material: str
    source_process: str
    monthly_quantity_kg: float
    current_route: str
    disposal_cost_per_month: float
    contamination_risk: str
    hazardous_flag: str
    department: str
    supplier: str
    supplier_takeback_available: str
    recycled_content_available: str
    notes: str | None


@dataclass(frozen=True)
class ScoreResult:
    evidence_quality_score: int
    risk_level: str
    confidence_score: int
    missing_data: list[str]
    human_review_required: bool


def _clean(value: object) -> str:
    return str(value or "").strip().lower()


def infer_missing_data(stream: StreamLike) -> list[str]:
    """Infer missing or weak evidence fields from the current Milestone 1 dataset."""
    missing: list[str] = []
    notes = _clean(stream.notes)

    if stream.monthly_quantity_kg <= 0:
        missing.append("measured monthly quantity or energy data")
    if stream.disposal_cost_per_month <= 0 and "return" not in _clean(stream.current_route):
        missing.append("current disposal or handling cost")
    if _clean(stream.contamination_risk) in {"unknown", "medium", "high"}:
        missing.append("contamination assessment")
    if _clean(stream.hazardous_flag) == "unknown":
        missing.append("confirmed hazardous status")
    if _clean(stream.supplier_takeback_available) == "unknown":
        missing.append("supplier take-back evidence")
    if _clean(stream.recycled_content_available) == "unknown":
        missing.append("recycled-content or secondary material evidence")
    if any(term in notes for term in ["unknown", "not always recorded", "not recorded", "requires", "needs", "unclear"]):
        missing.append("supporting operational evidence from notes")
    if "alloy" in notes and "not always recorded" in notes:
        missing.append("material grade or alloy segregation evidence")
    if "mixed" in _clean(stream.stream_name) or "mixed" in notes:
        missing.append("material segregation details")

    # Remove duplicates while preserving order.
    deduped: list[str] = []
    for item in missing:
        if item not in deduped:
            deduped.append(item)
    return deduped


def score_evidence_quality(stream: StreamLike) -> int:
    """Return an evidence quality score from 0 to 100.

    The MVP uses fields available in the synthetic dataset. Later milestones can replace
    this with a more formal evidence register.
    """
    score = 100
    contamination = _clean(stream.contamination_risk)
    hazardous = _clean(stream.hazardous_flag)
    supplier_takeback = _clean(stream.supplier_takeback_available)
    recycled_content = _clean(stream.recycled_content_available)
    notes = _clean(stream.notes)

    if stream.monthly_quantity_kg <= 0:
        score -= 15
    if stream.disposal_cost_per_month <= 0 and "return" not in _clean(stream.current_route):
        score -= 10
    if contamination == "medium":
        score -= 10
    elif contamination == "high":
        score -= 25
    elif contamination == "unknown":
        score -= 20
    if hazardous == "unknown":
        score -= 20
    elif hazardous == "true":
        score -= 15
    if supplier_takeback == "unknown":
        score -= 8
    if recycled_content == "unknown":
        score -= 7
    if any(term in notes for term in ["unknown", "not always recorded", "not recorded", "unclear"]):
        score -= 10
    if "mixed" in _clean(stream.stream_name) or "mixed" in notes:
        score -= 8

    return max(0, min(100, score))


def score_risk_level(stream: StreamLike) -> tuple[str, bool]:
    hazardous = _clean(stream.hazardous_flag)
    contamination = _clean(stream.contamination_risk)
    material = _clean(stream.material)

    if hazardous == "true" and contamination == "high":
        return "blocked", True
    if hazardous == "true":
        return "high", True
    if hazardous == "unknown" and contamination in {"medium", "high", "unknown"}:
        return "high", True
    if contamination == "high":
        return "high", True
    if material in {"chemicals/solvents", "electronic components"} and hazardous != "false":
        return "high", True
    if contamination == "medium" or hazardous == "unknown":
        return "medium", hazardous == "unknown"
    return "low", False


def score_confidence(
    stream: StreamLike,
    *,
    evidence_quality_score: int,
    risk_level: str,
    rule_strength: int,
    missing_data: list[str],
) -> int:
    score = evidence_quality_score
    score += rule_strength

    if risk_level == "medium":
        score -= 10
    elif risk_level == "high":
        score -= 25
    elif risk_level == "blocked":
        score -= 40

    score -= min(len(missing_data) * 3, 18)

    # Very small or zero-quantity streams can still be important, but the MVP should
    # avoid high confidence until a measured basis is available.
    if stream.monthly_quantity_kg <= 0:
        score -= 15

    return max(0, min(100, score))


def score_stream(stream: StreamLike, *, rule_strength: int = 10) -> ScoreResult:
    evidence_score = score_evidence_quality(stream)
    risk_level, human_review_required = score_risk_level(stream)
    missing_data = infer_missing_data(stream)
    confidence_score = score_confidence(
        stream,
        evidence_quality_score=evidence_score,
        risk_level=risk_level,
        rule_strength=rule_strength,
        missing_data=missing_data,
    )
    return ScoreResult(
        evidence_quality_score=evidence_score,
        risk_level=risk_level,
        confidence_score=confidence_score,
        missing_data=missing_data,
        human_review_required=human_review_required,
    )
