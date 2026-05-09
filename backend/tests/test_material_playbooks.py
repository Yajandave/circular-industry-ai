from app.circular_resolution.advanced_playbooks import (
    build_playbook_summary,
    get_advanced_playbook,
    list_advanced_playbooks,
)


def test_playbooks_cover_key_dataset_material_families():
    families = {playbook["material_family"] for playbook in list_advanced_playbooks()}
    expected = {
        "metals",
        "plastics",
        "cardboard/packaging",
        "wood/pallets",
        "chemicals/solvents",
        "textiles",
        "glass",
        "rubber",
        "electronic components",
        "organic/process residue",
        "process water",
        "energy/resource stream",
        "process mineral residue",
    }
    assert expected.issubset(families)


def test_grease_trap_maps_to_organic_playbook_with_controls():
    playbook = get_advanced_playbook("organic/process residue")
    text = " ".join(playbook.red_flags + playbook.claim_controls + playbook.routes_to_avoid).lower()
    assert "grease" in text or "fog" in text
    assert "classification" in text
    assert "authorised" in text


def test_waste_heat_playbook_does_not_frame_as_diversion():
    playbook = get_advanced_playbook("energy/resource stream")
    text = " ".join(playbook.routes_to_avoid + playbook.claim_controls).lower()
    assert "diversion" in text
    assert "carbon" in text
    assert "energy" in text


def test_playbook_summary_is_non_empty():
    summary = build_playbook_summary()
    assert summary["total_playbooks"] >= 13
    assert "metals" in summary["material_families"]
    assert "screening" in summary["coverage_note"].lower()
