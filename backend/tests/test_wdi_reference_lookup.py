import csv
from app.wdi_reference_lookup import lookup_reported_waste_code


def test_lookup_requires_configured_local_catalog(monkeypatch):
    monkeypatch.delenv("WDI_REFERENCE_CATALOG_CSV", raising=False)
    assert lookup_reported_waste_code("020110")["status"] == "catalog_not_configured"


def test_lookup_matches_reported_code_but_abstains_from_recommendation(tmp_path):
    path = tmp_path / "test-reference.csv"
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["waste_code", "reported_description", "reported_forms"])
        writer.writeheader()
        writer.writerow({"waste_code": "02 01 10", "reported_description": "waste metal", "reported_forms": "Solid"})
    result = lookup_reported_waste_code("020110", str(path))
    assert result["status"] == "found"
    assert result["matches"][0]["reported_description"] == "waste metal"
    assert result["verified_material_family"] is None
    assert result["recommended_circular_route"] is None
    assert result["decision_eligible"] is False


def test_invalid_code_cannot_trigger_lookup():
    assert lookup_reported_waste_code("anything")["status"] == "invalid_code"
