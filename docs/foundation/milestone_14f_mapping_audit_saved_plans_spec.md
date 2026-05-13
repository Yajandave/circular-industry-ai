# Milestone 14F — Mapping Audit Trail and Saved Mapping Plans Specification

## Purpose
Define how Circular Industry AI should record, reuse, and govern user-confirmed mapping decisions after the Data Profiler and User-Confirmed Mapping workflow.

This milestone is specification-only. It does not implement persistence, database migrations, frontend UI, or import endpoint code.

## Product Reason
If Circular Industry AI becomes a serious industrial circular economy decision-support product, mapping decisions cannot be treated as temporary UI state.

Real organisations may repeatedly upload files from:
- the same waste contractor
- the same procurement system
- the same site operations tracker
- the same supplier reporting template
- the same internal ESG or resource-flow spreadsheet

The product needs a controlled way to remember approved mapping structures while preserving auditability and evidence boundaries.

## Core Principle
Saved mapping plans improve repeatability.
Mapping audit trails protect trust.

A saved mapping plan must not mean:
- the source data is verified
- downstream outputs are verified
- future uploads are automatically safe without validation
- supplier compliance is confirmed
- environmental claims are substantiated

## Relationship to Previous Milestones
- 14C defines Data Profiler reliability risks.
- 14D defines user-confirmed mapping before import.
- 14E defines flexible Circular Core import using confirmed mappings.
- 14F defines how confirmed mappings can be saved, reused, audited, and governed.

## Required Concepts

### 1. Mapping Plan
A reusable structure that connects source column names to Circular Industry AI semantic roles.

Example fields:
- mapping plan ID
- mapping plan name
- organisation/site scope
- source template description
- created date
- last used date
- created by user in future versions
- target workspace
- semantic role mappings
- required role coverage
- known warnings
- version number
- status

### 2. Mapping Audit Record
A record of what happened during a specific import or mapping confirmation event.

Example fields:
- audit record ID
- dataset/file name
- upload timestamp
- profiler result summary
- suggested mappings
- user-confirmed mappings
- user changes
- ignored columns
- unresolved fields
- blocking errors
- warnings
- final import decision
- mapping plan used if any
- mapping plan version used
- generated analysis run ID if applicable

### 3. Mapping Plan Version
Saved plans should be versioned because source templates can change.

Versioning should capture:
- original mapping
- edited mapping
- date of change
- reason for change where available
- changed roles
- added or removed source columns
- new warnings
- compatibility with earlier uploads

## Mapping Plan States
A future implementation may use states such as:

- draft
- active
- deprecated
- needs_review
- archived
- rejected

## Audit Event Types
A future audit trail may include:

- profiler_suggestion_generated
- mapping_accepted_by_user
- mapping_changed_by_user
- column_ignored_by_user
- required_role_missing
- import_blocked
- import_confirmed
- mapping_plan_created
- mapping_plan_updated
- mapping_plan_reused
- mapping_plan_deprecated

## Saved Mapping Plan Workflow
A future user workflow should support:

1. User uploads a CSV.
2. System profiles the file.
3. System checks for a matching saved mapping plan.
4. If a possible plan exists, user is shown:
   - matched source columns
   - missing columns
   - new columns
   - changed confidence signals
   - compatibility warnings
5. User may:
   - use saved plan
   - adjust saved plan for this import only
   - update the saved plan
   - create a new saved plan
   - reject the suggested saved plan
6. System records the decision in an audit trail.

## Matching Rules for Saved Plans
A saved plan should not be reused blindly.

Potential matching signals:
- exact column name match
- high proportion of expected columns present
- source organisation/site match
- source template name
- contractor or supplier name
- previous upload pattern
- semantic role similarity

## Blocking Conditions for Reuse
Saved plan reuse should be blocked or require review when:
- required source columns are missing
- key columns have changed meaning
- duplicate required mappings appear
- critical semantic roles are unresolved
- the target workspace is different
- the source template appears incompatible

## Warning Conditions for Reuse
Saved plan reuse may continue with warnings when:
- optional columns are missing
- new unused columns appear
- column names changed slightly
- confidence is lower than previous uploads
- source data quality is weaker than usual
- some rows contain parse warnings

## Audit and Governance Requirements
The system should record:
- what the system suggested
- what the user accepted
- what the user changed
- what was ignored
- why import was blocked or allowed
- what warnings existed at the time
- which mapping plan version was used

The audit trail should help answer:
- Which file was imported?
- Which mapping was used?
- Who confirmed the mapping in future multi-user versions?
- What fields were missing?
- What warnings were present?
- Did the user override a low-confidence suggestion?
- Was the mapping reused from a prior plan?
- Which version of the mapping plan was used?

## Claim-Safety Boundary
A mapping audit trail is not evidence that the underlying data is accurate.

It only records:
- mapping decisions
- system warnings
- operator confirmations
- import control status

It does not verify:
- waste diversion
- cost savings
- carbon reduction
- supplier compliance
- ESG performance
- statutory EIA significance
- legal compliance

## Future Backend Considerations
Future backend work may require:
- mapping plan model
- mapping plan version model
- mapping audit event model
- import audit record model
- mapping compatibility checker
- saved plan retrieval endpoint
- plan create/update/deprecate endpoints
- audit export endpoint

## Future Frontend Considerations
Future UI work may require:
- saved plan selector
- plan compatibility summary
- mapping version comparison
- audit timeline
- warning review panel
- plan update confirmation modal
- import history view

## Non-Goals
This milestone does not implement:
- database persistence
- authentication
- multi-user audit identity
- frontend saved plan UI
- backend endpoints
- flexible import runtime logic
- production audit export

## Acceptance Criteria
14F is complete when the repo contains a clear specification for:
- saved mapping plans
- mapping plan states
- mapping plan versioning
- audit records
- audit event types
- saved plan reuse conditions
- blocking and warning conditions
- claim-safe governance boundaries

## Architecture Warning
Saved mapping plans must not become a shortcut around validation.

They should reduce repeated manual work while preserving:
- user confirmation
- import validation
- warning visibility
- audit traceability
- screening-output limitations
