from app.material_interpretation import interpret_material_family


def test_canonical_material_is_not_reinterpreted():
    result = interpret_material_family("metals")
    assert result["status"] == "already_canonical"
    assert result["proposed_family"] == "metals"


def test_unfamiliar_grade_is_proposed_not_automatically_applied():
    result = interpret_material_family("316L stainless steel machining swarf")
    assert result["proposed_family"] == "metals"
    assert result["status"] == "proposed_requires_operator_confirmation"


def test_unknown_description_remains_unresolved():
    assert interpret_material_family("Unknown")["proposed_family"] is None


def test_mixed_materials_cannot_be_forced_into_a_single_family():
    result = interpret_material_family("mixed waste metal and plastic")
    assert result["proposed_family"] is None


def test_unfamiliar_description_is_not_invented():
    assert interpret_material_family("wastes from mineral metalliferous excavation")["proposed_family"] is None
