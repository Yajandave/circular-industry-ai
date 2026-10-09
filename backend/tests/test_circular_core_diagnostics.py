from types import SimpleNamespace
from app.circular_core_diagnostics import inspect_circular_core

def obj(**kwargs):
    return SimpleNamespace(**kwargs)

def test_blocked_gate_and_exposure_are_not_achievable_savings():
    streams = [obj(stream_id="S1", monthly_quantity_kg=10, disposal_cost_per_month=100)]
    recs = [obj(stream_id="S1", risk_level="blocked", human_review_required=True,
                rule_applied="R001", estimated_annual_waste_diverted_kg=120,
                estimated_annual_disposal_cost_avoided=1200)]
    report = inspect_circular_core(streams, recs)
    assert report["achievable_savings"] is None
    assert report["achievable_diversion_kg"] is None
    assert all(c["status"] == "PASS" for c in report["checks"] if c["status"] != "NOT TESTED")
    assert report["review_required_count"] == 1

def test_blocked_without_review_is_detected():
    streams = [obj(stream_id="S1", monthly_quantity_kg=10, disposal_cost_per_month=100)]
    recs = [obj(stream_id="S1", risk_level="blocked", human_review_required=False,
                rule_applied="R001", estimated_annual_waste_diverted_kg=120,
                estimated_annual_disposal_cost_avoided=1200)]
    report = inspect_circular_core(streams, recs)
    checks = {c["name"]: c["status"] for c in report["checks"]}
    assert checks["high_and_blocked_review_gates"] == "FAIL"

def test_unlinked_recommendation_is_detected():
    streams = [obj(stream_id="S1", monthly_quantity_kg=10, disposal_cost_per_month=100)]
    recs = [obj(stream_id="S2", risk_level="low", human_review_required=False,
                rule_applied="R001", estimated_annual_waste_diverted_kg=120,
                estimated_annual_disposal_cost_avoided=1200)]
    checks = {c["name"]: c["status"] for c in inspect_circular_core(streams, recs)["checks"]}
    assert checks["recommendations_link_to_streams"] == "FAIL"
