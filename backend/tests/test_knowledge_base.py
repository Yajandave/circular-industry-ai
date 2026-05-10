"""Knowledge-base validation tests."""

from app.knowledge_base.loader import (
    load_collection,
    load_source_registry,
    validate_knowledge_base,
)


def test_source_registry_loads_seed_sources():
    registry = load_source_registry()
    sources = registry["sources"]
    source_ids = {source["source_id"] for source in sources}

    assert len(sources) >= 6
    assert "ceon_v1" in source_ids
    assert "olca_schema_v1" in source_ids
    assert "govuk_waste_classification_v1" in source_ids


def test_knowledge_base_structure_is_valid():
    summary = validate_knowledge_base()
    assert summary["valid"] is True, summary["issues"]
    assert summary["counts"]["materials"] >= 6
    assert summary["counts"]["circular_routes"] >= 5
    assert summary["counts"]["evidence_rules"] >= 3
    assert summary["counts"]["future_horizon"] >= 3


def test_materials_include_claim_boundaries_and_evidence():
    materials = load_collection("materials")
    for material in materials:
        assert material["evidence_required"]
        assert material["unsafe_claims"]
        assert material["default_claim_boundary"]
        assert material["source_references"]


def test_future_horizon_items_are_not_operational_claims():
    future_items = load_collection("future_horizon")
    for item in future_items:
        assert item["maturity"] in {"emerging", "research_stage", "pilot_ready", "available_now", "not_recommended"}
        assert item["claim_boundary"]
        assert item["do_not_claim"]
        assert item["current_use"] in {
            "future_watch_only",
            "future_horizon_and_supplier_data_structure",
            "future_watch_with_current_specialist_recovery_controls",
            "pilot_exploration",
        }
