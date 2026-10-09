"""Regression checks for incomplete and unexpected safety declarations.

These check the deterministic scoring boundary without persisting any data.
"""
from types import SimpleNamespace

import pytest
from app.scoring import score_risk_level, infer_missing_data, score_evidence_quality


def stream(hazard, contamination="low"):
    return SimpleNamespace(
        stream_id="AUDIT001", stream_name="Mixed process material",
        material="composite material", source_process="production",
        monthly_quantity_kg=100, disposal_cost_per_month=20,
        current_route="segregated holding", contamination_risk=contamination,
        hazardous_flag=hazard, department="Production", supplier="",
        supplier_takeback_available="unknown", recycled_content_available="unknown",
        notes="",
    )


@pytest.mark.parametrize("hazard", ["", " ", None, "pending", "yes", "n/a"])
def test_incomplete_hazard_status_requires_review(hazard):
    sample = stream(hazard)
    risk, review = score_risk_level(sample)
    assert review is True
    assert risk in {"medium", "high", "blocked"}
    assert "confirmed hazardous status" in infer_missing_data(sample)
    assert score_evidence_quality(sample) < score_evidence_quality(stream("false"))


@pytest.mark.parametrize("hazard", ["", None, "pending"])
def test_incomplete_hazard_with_high_contamination_is_high_risk(hazard):
    risk, review = score_risk_level(stream(hazard, "high"))
    assert risk == "high" and review is True


def test_known_false_hazard_not_automatically_blocked():
    risk, review = score_risk_level(stream("false"))
    assert risk == "low" and review is False
