"""Read-only Circular Core integrity checks. No decisions are recalculated or persisted."""
from collections import Counter
from math import isclose

from app.ruleset_release import RULESET_VERSION


def inspect_circular_core(streams, recommendations):
    checks = []
    def add(name, ok, detail=None):
        checks.append({"name": name, "status": "PASS" if ok else "FAIL", **({"detail": detail} if detail else {})})
    if not streams:
        return {
            "ruleset_version": RULESET_VERSION,
            "stream_count": 0, "recommendation_count": len(recommendations),
            "checks": [{"name": "dataset_available", "status": "NOT TESTED", "detail": "No loaded streams; load a dataset before checking current-run integrity."}],
            "limitations": "Inspects persisted outputs only; does not prove rule correctness or rerun rules.",
        }
    stream_ids = [s.stream_id for s in streams]
    rec_ids = [r.stream_id for r in recommendations]
    add("unique_stream_ids", len(stream_ids) == len(set(stream_ids)))
    if not recommendations:
        checks.append({"name": "recommendations_available", "status": "NOT TESTED", "detail": "Run the rules engine first."})
    else:
        add("unique_recommendation_ids", len(rec_ids) == len(set(rec_ids)))
        add("recommendations_link_to_streams", set(rec_ids).issubset(set(stream_ids)))
        add("one_recommendation_per_stream", Counter(rec_ids) == Counter(stream_ids))
        unsafe = [r for r in recommendations if str(r.risk_level).lower() in {"blocked", "high"}]
        add("high_and_blocked_review_gates", all(bool(r.human_review_required) for r in unsafe))
        add("rule_traceability_present", all(bool(getattr(r, "rule_applied", "")) for r in recommendations))
        by_id = {s.stream_id: s for s in streams}
        quantity_ok, cost_ok = True, True
        for r in recommendations:
            s = by_id.get(r.stream_id)
            if not s:
                continue
            # Legacy database labels encode throughput/cost exposure, NOT achievable benefit.
            quantity_ok &= isclose(float(r.estimated_annual_waste_diverted_kg), max(0, float(s.monthly_quantity_kg)) * 12, abs_tol=0.02)
            cost_ok &= isclose(float(r.estimated_annual_disposal_cost_avoided), max(0, float(s.disposal_cost_per_month)) * 12, abs_tol=0.02)
        add("legacy_quantity_equals_exposure", quantity_ok, "Legacy 'diverted' field is input throughput, not a forecast of achievable diversion.")
        add("legacy_cost_equals_exposure", cost_ok, "Legacy 'avoided' field is current cost exposure, not projected financial savings.")
    checks += [
        {"name": "full_rules_regression", "status": "NOT TESTED", "detail": "Requires dedicated fixture regression tests."},
        {"name": "evidence_register_accuracy", "status": "NOT TESTED", "detail": "Requires independent evidence expectations."},
        {"name": "supplier_loop_accuracy", "status": "NOT TESTED", "detail": "Requires supplier-specific verified input and expected outputs."},
    ]
    return {
        "ruleset_version": RULESET_VERSION,
        "stream_count": len(streams),
        "recommendation_count": len(recommendations),
        "risk_counts": dict(Counter(str(r.risk_level).lower() for r in recommendations)),
        "review_required_count": sum(bool(r.human_review_required) for r in recommendations),
        "annual_input_throughput_kg": round(sum(float(s.monthly_quantity_kg) for s in streams) * 12, 2),
        "annual_disposal_cost_exposure": round(sum(float(s.disposal_cost_per_month) for s in streams) * 12, 2),
        "achievable_diversion_kg": None, "achievable_savings": None,
        "checks": checks,
        "limitations": "Read-only persisted-data integrity checks; no underlying materials or supplier records included. Benefits not estimated.",
    }
