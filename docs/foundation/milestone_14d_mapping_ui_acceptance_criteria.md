# Milestone 14D — Mapping UI Acceptance Criteria

## Objective
Define the acceptance checks for a future user-confirmed mapping screen.

## Functional Acceptance Criteria
- The screen displays every detected CSV column.
- Each detected column shows sample values.
- The screen shows the system's suggested semantic role.
- The screen shows confidence level or warning status for each suggestion.
- The user can accept a suggested mapping.
- The user can change a suggested mapping.
- The user can mark a column as ignored.
- The user can identify unresolved or missing required fields.
- The system prevents import when required fields remain unresolved.
- The system allows optional fields to remain unmapped when safe.
- The final mapping state is explicit before import continues.

## Safety Acceptance Criteria
- The screen must not imply that system inference is verified.
- The screen must not imply that downstream results are verified impact, verified savings, verified diversion, verified carbon reduction, verified supplier compliance, or statutory EIA significance.
- The screen must include visible warning language when confidence is low.
- The screen must clearly separate system suggestions from user-confirmed decisions.

## Technical Acceptance Criteria
- Mapping state should be serialisable.
- Mapping decisions should be structured enough for later audit storage.
- Required roles should be validated deterministically.
- Mapping warnings should be generated consistently.
- The design should prepare for saved mapping plans in 14F.

## Future Test Cases
Future implementation should test:
- all required roles mapped
- one required role missing
- duplicate candidate mappings
- low-confidence system suggestion accepted by user
- system suggestion changed by user
- ignored optional column
- invalid mapping combination blocked
- sparse CSV with weak sample values
- CSV with ambiguous headers
- CSV with unsupported units

## Definition of Done
14D is done when the specification makes it clear how the mapping confirmation layer should behave before any flexible import or saved mapping plan is implemented.
