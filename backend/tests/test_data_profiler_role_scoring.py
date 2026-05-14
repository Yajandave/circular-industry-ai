import pandas as pd

from app.data_profiler_role_scoring import normalise, role_candidates


def test_normalise_cleans_headers_without_losing_claim_sensitive_symbols():
    assert normalise(" Monthly_Disposal-Cost (£) ") == "monthly disposal cost £"


def test_role_candidates_maps_waste_material_header_to_material_role():
    candidates = role_candidates("Waste Material", pd.Series(["Steel", "Plastic", "Cardboard"]))

    assert candidates[0]["role"] == "material"
    assert candidates[0]["confidence"] >= 85


def test_role_candidates_maps_vendor_name_to_supplier_role():
    candidates = role_candidates("Vendor Name", pd.Series(["ABC Metals", "Green Plastics"]))

    assert candidates[0]["role"] == "supplier"


def test_role_candidates_uses_numeric_type_signal_for_disposal_cost():
    candidates = role_candidates("Monthly Disposal Cost", pd.Series(["1200", "800", "300"]))

    assert candidates[0]["role"] == "disposal_cost_per_month"
