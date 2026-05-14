import pytest

from app.mapping_validation import validate_confirmed_mapping
from app.schemas import ConfirmedMappingItem, ConfirmedMappingValidationRequest


def _request(mappings):
    return ConfirmedMappingValidationRequest(target_workspace="circular-core", mappings=mappings)


def test_confirmed_mapping_ready_when_required_roles_are_confirmed():
    report = validate_confirmed_mapping(
        _request(
            [
                ConfirmedMappingItem(source_column="Waste Material", target_role="material", mapping_state="accepted_by_user", confidence=96, user_confirmed=True),
                ConfirmedMappingItem(source_column="Monthly Weight", target_role="quantity", mapping_state="accepted_by_user", confidence=91, user_confirmed=True),
                ConfirmedMappingItem(source_column="Disposal Method", target_role="current_route", mapping_state="changed_by_user", confidence=88, user_confirmed=True),
            ]
        )
    )

    assert report["import_status"] == "ready"
    assert report["blocking_errors"] == []
    assert {item["role"] for item in report["resolved_required_roles"]} == {"material", "quantity", "current_route"}


def test_confirmed_mapping_blocks_when_required_role_is_only_suggested():
    report = validate_confirmed_mapping(
        _request(
            [
                ConfirmedMappingItem(source_column="Waste Material", target_role="material", mapping_state="accepted_by_user", confidence=96, user_confirmed=True),
                ConfirmedMappingItem(source_column="Monthly Weight", target_role="quantity", mapping_state="suggested_by_system", confidence=91, user_confirmed=False),
                ConfirmedMappingItem(source_column="Disposal Method", target_role="current_route", mapping_state="accepted_by_user", confidence=88, user_confirmed=True),
            ]
        )
    )

    assert report["import_status"] == "blocked"
    assert any(error["code"] == "required_role_not_confirmed" for error in report["blocking_errors"])
    assert any(item["role"] == "quantity" for item in report["missing_required_roles"])


def test_confirmed_mapping_blocks_duplicate_confirmed_target_roles():
    report = validate_confirmed_mapping(
        _request(
            [
                ConfirmedMappingItem(source_column="Waste Material", target_role="material", mapping_state="accepted_by_user", confidence=96, user_confirmed=True),
                ConfirmedMappingItem(source_column="Material Type", target_role="material", mapping_state="changed_by_user", confidence=80, user_confirmed=True),
                ConfirmedMappingItem(source_column="Monthly Weight", target_role="quantity", mapping_state="accepted_by_user", confidence=91, user_confirmed=True),
                ConfirmedMappingItem(source_column="Disposal Method", target_role="current_route", mapping_state="accepted_by_user", confidence=88, user_confirmed=True),
            ]
        )
    )

    assert report["import_status"] == "blocked"
    assert any(error["code"] == "duplicate_confirmed_target_role" for error in report["blocking_errors"])


def test_confirmed_mapping_warns_on_low_confidence_user_confirmed_mapping():
    report = validate_confirmed_mapping(
        _request(
            [
                ConfirmedMappingItem(source_column="Waste Material", target_role="material", mapping_state="accepted_by_user", confidence=96, user_confirmed=True),
                ConfirmedMappingItem(source_column="Monthly Weight", target_role="quantity", mapping_state="accepted_by_user", confidence=58, user_confirmed=True),
                ConfirmedMappingItem(source_column="Disposal Method", target_role="current_route", mapping_state="accepted_by_user", confidence=88, user_confirmed=True),
            ]
        )
    )

    assert report["import_status"] == "ready_with_warnings"
    assert any(warning["code"] == "low_confidence_confirmed_mapping" for warning in report["warnings"])


def test_confirmed_mapping_blocks_unknown_target_role():
    report = validate_confirmed_mapping(
        _request(
            [
                ConfirmedMappingItem(source_column="Waste Material", target_role="material", mapping_state="accepted_by_user", confidence=96, user_confirmed=True),
                ConfirmedMappingItem(source_column="Monthly Weight", target_role="quantity", mapping_state="accepted_by_user", confidence=91, user_confirmed=True),
                ConfirmedMappingItem(source_column="Mystery", target_role="unsupported_role", mapping_state="accepted_by_user", confidence=90, user_confirmed=True),
            ]
        )
    )

    assert report["import_status"] == "blocked"
    assert any(error["code"] == "unknown_target_role" for error in report["blocking_errors"])


def test_confirmed_mapping_rejects_unknown_workspace():
    with pytest.raises(ValueError, match="Unknown target workspace"):
        validate_confirmed_mapping(ConfirmedMappingValidationRequest(target_workspace="unknown", mappings=[]))
