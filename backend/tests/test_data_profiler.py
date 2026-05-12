from app.data_profiler import profile_csv_bytes


def test_profiler_maps_alternative_column_names_to_circular_core_roles():
    csv = b"""Waste Material,Weight per Month,Vendor Name,Disposal Method,Monthly Disposal Cost
Steel,500,ABC Metals,Recycling,1200
Plastic,200,Green Plastics,Disposal,800
"""
    report = profile_csv_bytes(csv, dataset_label="alternative_columns.csv")
    mapped = {item["role"]: item["source_column"] for item in report["role_mapping"]}

    assert report["detected_workspace"] == "circular-core"
    assert mapped["material"] == "Waste Material"
    assert mapped["quantity"] == "Weight per Month"
    assert mapped["supplier"] == "Vendor Name"
    assert mapped["current_route"] == "Disposal Method"
    assert mapped["disposal_cost_per_month"] == "Monthly Disposal Cost"
    assert any("hazardous" in item.lower() for item in report["unavailable_analysis_routes"])


def test_profiler_does_not_invent_missing_fields():
    csv = b"""Material,Quantity,Route
Steel,500,Recycling
"""
    report = profile_csv_bytes(csv, dataset_label="missing_fields.csv")
    roles = {item["role"] for item in report["role_mapping"]}

    assert "hazardous_flag" not in roles
    assert "contamination_risk" not in roles
    assert any("hazardous" in item.lower() for item in report["unavailable_analysis_routes"])
    assert any("contamination" in item.lower() for item in report["unavailable_analysis_routes"])


def test_profiler_routes_claim_dataset_without_forcing_circular_core():
    csv = b"""Claim,Product,Evidence,Verification Status
Carbon neutral,Product A,Offset certificate,Pending
Recyclable,Product B,Lab test,Verified
"""
    report = profile_csv_bytes(csv, dataset_label="claims.csv")
    mapped = {item["role"]: item["source_column"] for item in report["role_mapping"]}

    assert report["detected_workspace"] == "greenwashing-claims"
    assert mapped["claim_text"] == "Claim"
    assert mapped["evidence"] == "Evidence"
