from types import SimpleNamespace
from app.rules_engine import recommend_for_stream

def sample(**overrides):
    data = dict(stream_id="AUDIT",stream_name="Industrial material",material="metals",
        source_process="manufacturing",monthly_quantity_kg=500,current_route="storage",
        disposal_cost_per_month=200,contamination_risk="low",hazardous_flag="false",
        department="Operations",supplier="Unknown",
        supplier_takeback_available="unknown",recycled_content_available="unknown",notes="")
    data.update(overrides)
    return recommend_for_stream(SimpleNamespace(**data))

def test_unknown_contamination_requires_review_and_no_route_selection():
    result=sample(contamination_risk="unknown")
    assert result.human_review_required is True
    assert result.risk_level != "low"
    assert result.circular_strategy_category == "human review required"
    assert "contamination assessment" in result.missing_data

def test_unidentified_material_requires_identity_first():
    result=sample(material="unidentified composite")
    assert result.human_review_required is True
    assert "material identity" in result.missing_data
    assert "Needs more information" in result.recommended_circular_action

def test_missing_hazard_does_not_offer_metal_recycling():
    result=sample(hazardous_flag="")
    assert result.human_review_required is True
    assert result.circular_strategy_category == "human review required"
    assert "hazardous status" in result.recommended_circular_action

def test_confirmed_clean_metal_still_reaches_metal_rule():
    result=sample()
    assert result.rule_applied == "R005_METAL_CLOSED_LOOP"
