import warnings

import pytest

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

# Milestone 16A — Data Profiler edge-case hardening tests

def _profile_without_user_warnings(csv: bytes, dataset_label: str):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        report = profile_csv_bytes(csv, dataset_label=dataset_label)

    user_warnings = [warning for warning in caught if issubclass(warning.category, UserWarning)]
    assert user_warnings == []
    return report


def test_profiler_detects_date_columns_without_pandas_format_warning():
    csv = b"""Date,Material,Quantity,Route
01/02/2026,Steel,500,Recycling
15/02/2026,Plastic,200,Disposal
"""
    report = _profile_without_user_warnings(csv, dataset_label="uk_dates.csv")

    date_column = next(column for column in report["columns"] if column["original_name"] == "Date")
    assert date_column["inferred_data_type"] == "date"
    assert report["detected_workspace"] == "circular-core"


def test_profiler_does_not_classify_mixed_operational_text_as_date():
    csv = b"""Review Period,Material,Quantity,Route
Q1 2026,Steel,500,Recycling
not confirmed,Plastic,200,Disposal
"""
    report = _profile_without_user_warnings(csv, dataset_label="mixed_operational_text.csv")

    review_column = next(column for column in report["columns"] if column["original_name"] == "Review Period")
    assert review_column["inferred_data_type"] != "date"


def test_profiler_rejects_empty_upload_with_clear_error():
    with pytest.raises(ValueError, match="empty"):
        profile_csv_bytes(b"", dataset_label="empty.csv")


def test_profiler_handles_header_only_csv_without_crashing_or_warning():
    csv = b"Material,Quantity,Route\n"
    report = _profile_without_user_warnings(csv, dataset_label="header_only.csv")

    assert report["total_rows"] == 0
    assert report["total_columns"] == 3
    assert all(column["inferred_data_type"] == "empty" for column in report["columns"])


def test_profiler_reports_duplicate_rows_for_import_quality_review():
    csv = b"""Material,Quantity,Route
Steel,500,Recycling
Steel,500,Recycling
Plastic,200,Disposal
"""
    report = _profile_without_user_warnings(csv, dataset_label="duplicate_rows.csv")

    assert report["duplicate_rows"] == 1
    assert report["detected_workspace"] == "circular-core"

