# Milestone 14F — Saved Mapping Plan Data Contract

## Objective
Define a future data contract for saved mapping plans and mapping audit records.

This is an illustrative contract. It is not a locked schema or implementation mandate.

## Saved Mapping Plan Object

```json
{
  "mapping_plan_id": "map_plan_001",
  "name": "Example Waste Contractor Monthly Export",
  "status": "active",
  "version": 1,
  "target_workspace": "circular_core",
  "scope": {
    "organisation_id": null,
    "site_id": null,
    "supplier_name": null,
    "source_system": null
  },
  "source_signature": {
    "expected_columns": [],
    "required_columns": [],
    "optional_columns": []
  },
  "semantic_mappings": [],
  "known_warnings": [],
  "created_at": null,
  "updated_at": null,
  "last_used_at": null
}
```

## Semantic Mapping Item

```json
{
  "source_column": "Monthly Weight",
  "target_role": "monthly_quantity",
  "required": true,
  "last_confidence": "high",
  "normalisation_rule": null,
  "unit_assumption": null,
  "notes": null
}
```

## Mapping Plan Compatibility Result

```json
{
  "compatible": true,
  "reuse_status": "safe_to_review",
  "matched_columns": [],
  "missing_required_columns": [],
  "missing_optional_columns": [],
  "new_columns": [],
  "warnings": [],
  "blocking_errors": []
}
```

## Mapping Audit Record

```json
{
  "mapping_audit_id": "mapping_audit_001",
  "file_name": "example.csv",
  "upload_timestamp": null,
  "target_workspace": "circular_core",
  "mapping_plan_id": null,
  "mapping_plan_version": null,
  "profiler_summary": {},
  "system_suggestions": [],
  "user_confirmed_mappings": [],
  "user_changes": [],
  "ignored_columns": [],
  "unresolved_roles": [],
  "blocking_errors": [],
  "warnings": [],
  "final_decision": "confirmed | blocked | cancelled | saved_as_draft",
  "analysis_run_id": null
}
```

## Audit Event Object

```json
{
  "event_type": "mapping_changed_by_user",
  "timestamp": null,
  "source_column": "Vendor Name",
  "previous_target_role": "department",
  "new_target_role": "supplier",
  "reason": null,
  "warning_context": []
}
```

## Required Behaviours

### Saved Plan Creation
A saved mapping plan should only be created after:
- mapping has been reviewed by the user
- required roles are resolved
- warnings are visible
- user chooses to save the mapping structure

### Saved Plan Reuse
Saved plan reuse should always perform compatibility checks against the new uploaded file.

### Saved Plan Update
Updating a saved plan should create a new version rather than silently mutating historical mapping evidence.

### Audit Record Creation
Every mapping confirmation or blocked import should create an audit record in future implementation.

## Future Test Cases
Future implementation should test:

- create saved mapping plan after confirmed mapping
- reuse exact matching plan
- reuse plan with optional column missing
- block plan reuse when required column missing
- warn when new source column appears
- create new plan version after update
- preserve old plan version in historical audit
- record user changed mapping
- record ignored column
- record import blocked
- record import confirmed
- record low-confidence suggestion accepted
- record mapping plan deprecated

## Data Governance Notes
Saved mapping plans should improve operational consistency but should not become evidence of source-data accuracy.

The system must continue to distinguish:
- system suggestion
- user confirmation
- source evidence
- external verification
- screening estimate
- verified impact

## Definition of Done
This contract is sufficient when future implementation can design persistence and API endpoints without confusing:
- mapping reuse with verification
- user confirmation with audit assurance
- screening outputs with verified sustainability claims
