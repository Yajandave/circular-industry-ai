"""User-confirmed mapping validation for Data Profiler outputs.

This module does not import data into Circular Core. It only validates whether
a user-confirmed mapping set is structurally ready for a future import step.
"""

from __future__ import annotations

from app.data_profiler_config import GOVERNANCE_NOTE, ROLE_ALIASES, ROLE_LABELS, WORKSPACE_RULES


CONFIRMED_MAPPING_STATES = {"accepted_by_user", "changed_by_user"}
NON_IMPORT_READY_STATES = {"suggested_by_system", "unresolved", "needs_review", "missing_required_role"}


def validate_confirmed_mapping(payload) -> dict:
    """Validate user-confirmed mappings for a target workspace.

    The payload is expected to be a Pydantic model with `target_workspace` and
    `mappings` fields, but the function deliberately uses duck typing so tests
    and future callers can reuse the logic easily.
    """

    target_workspace = payload.target_workspace
    if target_workspace not in WORKSPACE_RULES:
        raise ValueError(f"Unknown target workspace: {target_workspace}")

    workspace_rule = WORKSPACE_RULES[target_workspace]
    required_roles = list(workspace_rule.get("required", []))
    valid_roles = set(ROLE_ALIASES)

    blocking_errors: list[dict] = []
    warnings: list[dict] = []
    accepted_mappings: list[dict] = []
    ignored_columns: list[str] = []
    unresolved_roles: set[str] = set(required_roles)

    role_to_sources: dict[str, list[str]] = {}

    for mapping in payload.mappings:
        source_column = mapping.source_column.strip()
        target_role = mapping.target_role.strip() if mapping.target_role else None
        state = mapping.mapping_state

        if state == "ignored_by_user":
            ignored_columns.append(source_column)
            continue

        if target_role and target_role not in valid_roles:
            blocking_errors.append(
                {
                    "code": "unknown_target_role",
                    "source_column": source_column,
                    "target_role": target_role,
                    "message": f"Target role '{target_role}' is not recognised by the Data Profiler contract.",
                }
            )
            continue

        if target_role:
            role_to_sources.setdefault(target_role, []).append(source_column)

        if target_role in required_roles and state in CONFIRMED_MAPPING_STATES and mapping.user_confirmed:
            unresolved_roles.discard(target_role)
            accepted_mappings.append(_accepted_mapping_dict(mapping))
            if mapping.confidence < 60:
                warnings.append(
                    {
                        "code": "low_confidence_confirmed_mapping",
                        "source_column": source_column,
                        "target_role": target_role,
                        "message": "A low-confidence mapping was confirmed by the user and should be reviewed before import.",
                    }
                )
            continue

        if target_role in required_roles and state in NON_IMPORT_READY_STATES:
            blocking_errors.append(
                {
                    "code": "required_role_not_confirmed",
                    "source_column": source_column,
                    "target_role": target_role,
                    "message": f"Required role '{target_role}' has not been confirmed by the user.",
                }
            )
        elif target_role and state in CONFIRMED_MAPPING_STATES and mapping.user_confirmed:
            accepted_mappings.append(_accepted_mapping_dict(mapping))
            if mapping.confidence < 60:
                warnings.append(
                    {
                        "code": "low_confidence_confirmed_mapping",
                        "source_column": source_column,
                        "target_role": target_role,
                        "message": "A low-confidence optional mapping was confirmed by the user.",
                    }
                )

    for role, sources in role_to_sources.items():
        confirmed_sources = [
            mapping.source_column
            for mapping in payload.mappings
            if mapping.target_role == role and mapping.mapping_state in CONFIRMED_MAPPING_STATES and mapping.user_confirmed
        ]
        if len(confirmed_sources) > 1:
            blocking_errors.append(
                {
                    "code": "duplicate_confirmed_target_role",
                    "target_role": role,
                    "source_columns": confirmed_sources,
                    "message": f"Multiple confirmed source columns map to target role '{role}'.",
                }
            )

    for role in sorted(unresolved_roles):
        blocking_errors.append(
            {
                "code": "missing_required_role",
                "target_role": role,
                "message": f"Required role '{role}' is missing or unresolved for {workspace_rule['label']}.",
            }
        )

    import_status = "blocked" if blocking_errors else ("ready_with_warnings" if warnings else "ready")

    return {
        "target_workspace": target_workspace,
        "target_workspace_label": workspace_rule["label"],
        "import_status": import_status,
        "required_roles": [{"role": role, "label": ROLE_LABELS.get(role, role)} for role in required_roles],
        "resolved_required_roles": [
            {"role": role, "label": ROLE_LABELS.get(role, role)}
            for role in required_roles
            if role not in unresolved_roles
        ],
        "missing_required_roles": [
            {"role": role, "label": ROLE_LABELS.get(role, role)}
            for role in sorted(unresolved_roles)
        ],
        "accepted_mappings": accepted_mappings,
        "ignored_columns": ignored_columns,
        "blocking_errors": blocking_errors,
        "warnings": warnings,
        "governance_note": GOVERNANCE_NOTE,
    }


def _accepted_mapping_dict(mapping) -> dict:
    return {
        "source_column": mapping.source_column,
        "target_role": mapping.target_role,
        "target_role_label": ROLE_LABELS.get(mapping.target_role, mapping.target_role),
        "mapping_state": mapping.mapping_state,
        "confidence": mapping.confidence,
        "user_confirmed": mapping.user_confirmed,
    }
