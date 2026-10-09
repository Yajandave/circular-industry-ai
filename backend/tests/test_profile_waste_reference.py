from app.profile_waste_reference import profile_with_waste_reference


def test_csv_profile_without_code_column_preserves_existing_profiler():
    result = profile_with_waste_reference(b"material,monthly_quantity_kg,current_route\nmetals,100,recycling\n", "input.csv")
    assert result["profile"]["total_rows"] == 1
    assert result["reference_status"] == "no_unambiguous_waste_code_column"


def test_waste_code_lookups_without_catalog_do_not_generate_decisions(monkeypatch):
    monkeypatch.delenv("WDI_REFERENCE_CATALOG_CSV", raising=False)
    result = profile_with_waste_reference(b"Waste Code,description\n020110,waste metal\n", "ea.csv")
    assert result["waste_code_column"] == "Waste Code"
    assert result["waste_code_lookups"][0]["status"] == "catalog_not_configured"
