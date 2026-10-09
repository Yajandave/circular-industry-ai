from app.external_waste_assessment import assess_external_waste_row, assess_external_waste_rows


def test_reported_tonnes_are_not_treated_as_monthly_factory_quantity():
    result = assess_external_waste_row({
        "challenge_id": "EA25-RECEIVED-001",
        "Waste Code": "01 01 01",
        "EWC Waste Desc": "wastes from mineral metalliferous excavation",
        "Tonnes Received": "3.84",
        "Tonnes Removed": "",
    })
    assert result["reported_movement_kg"] == 3840
    assert result["monthly_stream_quantity_kg"] is None
    assert result["route_recommendation"] is None
    assert result["material_family"] is None
    assert result["decision_status"] == "requires_mapping_and_competent_evidence_review"


def test_does_not_invent_a_quantity_if_both_movement_directions_are_present():
    result = assess_external_waste_row({
        "Waste Code": "17 04 05", "EWC Waste Desc": "iron and steel",
        "Tonnes Received": "1.2", "Tonnes Removed": "2.3",
    })
    assert result["reported_movement_kg"] is None
    assert result["warnings"]


def test_reported_asterisk_does_not_establish_competent_hazard_classification():
    result = assess_external_waste_row({
        "Waste Code": "14 06 03*", "EWC Waste Desc": "other solvents",
        "Tonnes Removed": "0.5",
    })
    assert result["reported_hazardous_code_asterisk"] is True
    assert result["route_recommendation"] is None
    assert "competent_hazardous_waste_classification" in result["missing_decision_inputs"]


def test_batch_does_not_generate_unsupported_routes():
    result = assess_external_waste_rows([{"Waste Code": "17 04 05", "Tonnes Received": "2"}])
    assert result["total_records"] == 1
    assert result["recommendations_generated"] == 0
    assert result["records_requiring_review"] == 1
