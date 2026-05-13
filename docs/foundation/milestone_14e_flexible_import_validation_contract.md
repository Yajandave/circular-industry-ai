# Milestone 14E — Flexible Import Validation Contract

## Objective
Define the future validation contract for importing user-confirmed mapped datasets into Circular Core.

## Validation Contract Shape
A future backend validation object may include:

```json
{
  "import_status": "blocked | accepted | accepted_with_warnings",
  "required_roles_resolved": true,
  "blocking_errors": [],
  "warnings": [],
  "row_counts": {
    "total_rows": 0,
    "accepted_rows": 0,
    "rejected_rows": 0,
    "warning_rows": 0
  },
  "mapping_summary": [],
  "row_issue_summary": []
}
```

This is illustrative, not a locked implementation requirement.

## Mapping Validation Rules

### Required Role Rules
- Required roles must be present before import.
- Required roles must be user-confirmed.
- Required roles must not be mapped to empty-only columns.
- Required roles must not conflict with another required role.

### Optional Role Rules
- Optional roles may be absent.
- Optional roles should not block import.
- Optional roles should still preserve warnings where values are weak.

### Conflict Rules
Import should block when:
- two required target roles use the same source column without an approved reason
- one source column is mapped to incompatible meanings
- a required numeric field contains no parseable numeric values
- a required role is marked unresolved or ignored

## Row-Level Validation

### Critical Row Issues
Rows may be rejected or blocked when:
- material or stream identifier is missing
- current route is missing
- quantity field is unusable where required
- hazardous status is contradictory
- row is structurally empty

### Non-Critical Row Issues
Rows may continue with warnings when:
- optional supplier is missing
- optional department is missing
- unit is unsupported but raw quantity is preserved
- notes are missing
- cost is missing where cost analysis is not required

## Numeric and Unit Handling
The future import layer should:
- parse numeric values deterministically
- retain raw values
- separate parsed values from raw values
- warn on mixed units
- warn on unsupported units
- avoid automatic conversion unless rules are explicit

## Boolean Handling
Fields such as hazardous flag, supplier take-back, and recycled-content availability should not rely on fragile assumptions.

Supported values should be explicit, for example:
- yes/no
- true/false
- y/n
- 1/0

Ambiguous values should create warnings or unresolved states, not hidden assumptions.

## Evidence and Claim Safety
Validation should track whether imported data is:
- user-provided
- system-normalised
- inferred
- missing
- unsupported
- confirmed by user
- verified by external evidence

The system must not treat user confirmation as external verification.

## Future Test Cases
Implementation should eventually test:

- valid mapped import
- missing required material role
- missing required route role
- duplicate required mapping
- numeric field with commas
- numeric field with currency symbols
- mixed units in one column
- unsupported units
- empty rows
- sparse rows
- optional supplier missing
- low-confidence mapping accepted by user
- ignored optional columns
- ambiguous boolean values
- hazardous flag conflicts
- raw values preserved after warning

## Definition of Done
This validation contract is sufficient when a future developer can implement flexible Circular Core import without weakening:
- evidence control
- mapping auditability
- claim-safety boundaries
- rules-engine authority
- screening-output limitations
