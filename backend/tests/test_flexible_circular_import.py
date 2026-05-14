from app.flexible_circular_import import build_flexible_circular_core_import
from app.schemas import (
    ConfirmedMappingItem,
    ConfirmedMappingValidationRequest,
    FlexibleCircularCoreImportRequest,
)


def _ready_mapping(*, include_stream_id: bool = True, unit_role: bool = True):
    mappings = []
    if include_stream_id:
        mappings.append(ConfirmedMappingItem(source_column="Stream ID", target_role="stream_id", mapping_state="accepted_by_user", confidence=90, user_confirmed=True))

    mappings.extend(
        [
            ConfirmedMappingItem(source_column="Waste Material", target_role="material", mapping_state="accepted_by_user", confidence=99, user_confirmed=True),
            ConfirmedMappingItem(source_column="Monthly Weight", target_role="quantity", mapping_state="accepted_by_user", confidence=96, user_confirmed=True),
            ConfirmedMappingItem(source_column="Disposal Method", target_role="current_route", mapping_state="accepted_by_user", confidence=99, user_confirmed=True),
            ConfirmedMappingItem(source_column="Waste Stream", target_role="stream_name", mapping_state="accepted_by_user", confidence=86, user_confirmed=True),
            ConfirmedMappingItem(source_column="Monthly Disposal Cost", target_role="disposal_cost_per_month", mapping_state="accepted_by_user", confidence=86, user_confirmed=True),
        ]
    )

    if unit_role:
        mappings.append(ConfirmedMappingItem(source_column="Weight Unit", target_role="quantity_unit", mapping_state="accepted_by_user", confidence=86, user_confirmed=True))

    return ConfirmedMappingValidationRequest(target_workspace="circular-core", mappings=mappings)


def test_flexible_import_builds_draft_rows_from_ready_mapping():
    payload = FlexibleCircularCoreImportRequest(
        mapping_validation=_ready_mapping(),
        source_rows=[
            {
                "Stream ID": "S001",
                "Waste Stream": "Steel offcuts",
                "Waste Material": "Steel",
                "Monthly Weight": "1250",
                "Weight Unit": "kg",
                "Disposal Method": "Recycling",
                "Monthly Disposal Cost": "780",
            }
        ],
    )

    report = build_flexible_circular_core_import(payload)

    assert report["import_status"] == "ready"
    assert report["draft_row_count"] == 1
    assert report["draft_rows"][0]["stream_id"] == "S001"
    assert report["draft_rows"][0]["material"] == "Steel"
    assert report["draft_rows"][0]["monthly_quantity_kg"] == 1250
    assert report["draft_rows"][0]["current_route"] == "Recycling"
    assert report["draft_rows"][0]["draft_status"] == "draft_only_not_imported"
    assert report["blocking_errors"] == []


def test_flexible_import_blocks_when_mapping_validation_is_blocked():
    payload = FlexibleCircularCoreImportRequest(
        mapping_validation=ConfirmedMappingValidationRequest(
            target_workspace="circular-core",
            mappings=[
                ConfirmedMappingItem(source_column="Waste Material", target_role="material", mapping_state="accepted_by_user", confidence=99, user_confirmed=True),
                ConfirmedMappingItem(source_column="Monthly Weight", target_role="quantity", mapping_state="accepted_by_user", confidence=96, user_confirmed=True),
                ConfirmedMappingItem(source_column="Disposal Method", target_role="current_route", mapping_state="suggested_by_system", confidence=99, user_confirmed=False),
            ],
        ),
        source_rows=[
            {"Waste Material": "Steel", "Monthly Weight": "1250", "Disposal Method": "Recycling"}
        ],
    )

    report = build_flexible_circular_core_import(payload)

    assert report["import_status"] == "blocked"
    assert report["draft_rows"] == []
    assert any(error["code"] == "required_role_not_confirmed" for error in report["blocking_errors"])


def test_flexible_import_generates_draft_stream_id_when_not_mapped():
    payload = FlexibleCircularCoreImportRequest(
        mapping_validation=_ready_mapping(include_stream_id=False),
        source_rows=[
            {
                "Waste Stream": "Steel offcuts",
                "Waste Material": "Steel",
                "Monthly Weight": "1250",
                "Weight Unit": "kg",
                "Disposal Method": "Recycling",
                "Monthly Disposal Cost": "780",
            }
        ],
    )

    report = build_flexible_circular_core_import(payload)

    assert report["import_status"] == "ready_with_warnings"
    assert report["draft_rows"][0]["stream_id"] == "DRAFT-0001"
    assert any(warning["code"] == "generated_stream_id" for warning in report["row_warnings"])


def test_flexible_import_converts_tonnes_to_kg():
    payload = FlexibleCircularCoreImportRequest(
        mapping_validation=_ready_mapping(),
        source_rows=[
            {
                "Stream ID": "S010",
                "Waste Stream": "Cardboard",
                "Waste Material": "Cardboard",
                "Monthly Weight": "1.5",
                "Weight Unit": "tonnes",
                "Disposal Method": "Recycling",
                "Monthly Disposal Cost": "100",
            }
        ],
    )

    report = build_flexible_circular_core_import(payload)

    assert report["draft_rows"][0]["monthly_quantity_kg"] == 1500


def test_flexible_import_warns_on_invalid_quantity():
    payload = FlexibleCircularCoreImportRequest(
        mapping_validation=_ready_mapping(),
        source_rows=[
            {
                "Stream ID": "S011",
                "Waste Stream": "Plastic",
                "Waste Material": "Plastic",
                "Monthly Weight": "unknown",
                "Weight Unit": "kg",
                "Disposal Method": "General waste",
                "Monthly Disposal Cost": "not available",
            }
        ],
    )

    report = build_flexible_circular_core_import(payload)

    assert report["import_status"] == "ready_with_warnings"
    assert report["draft_rows"][0]["monthly_quantity_kg"] == 0
    assert report["draft_rows"][0]["disposal_cost_per_month"] == 0
    assert any(warning["code"] == "invalid_quantity" for warning in report["row_warnings"])
    assert any(warning["code"] == "invalid_numeric_value" for warning in report["row_warnings"])
