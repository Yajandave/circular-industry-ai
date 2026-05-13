# Milestone 14D — User-Confirmed Mapping Screen Specification

## Purpose
Define the user-confirmed mapping workflow that sits between automated CSV profiling and operational import into Circular Core.

This milestone does not implement the UI yet. It defines the product, governance, and technical behaviour required before code is added.

## Product Reason
The Data Profiler may infer semantic roles, column meanings, likely workspace routes, and missing fields. However, inferred mapping must not be treated as verified input.

For a serious industrial circular economy decision-support product, the system must create a trust checkpoint where the operator reviews, confirms, adjusts, or rejects mappings before downstream analysis.

## Core Principle
System inference is advisory.
Operator confirmation is the control point.
Rules-engine outputs remain screening outputs unless supported by verified evidence.

## Required User Workflow
1. User uploads a CSV.
2. Data Profiler analyses columns, completeness, data types, and likely semantic roles.
3. System presents proposed mappings with confidence indicators.
4. User reviews each mapped field.
5. User can:
   - accept a suggested mapping
   - change a mapping
   - mark a column as not used
   - flag uncertainty
   - identify missing required fields
6. System blocks operational import when required roles are unresolved.
7. Confirmed mapping is passed to the future flexible import layer.
8. Mapping decisions are saved into an audit structure in later milestone 14F.

## Required Mapping States
- suggested_by_system
- accepted_by_user
- changed_by_user
- ignored_by_user
- missing_required_role
- unresolved
- needs_review

## Required UI Sections
### 1. Import Summary
Shows:
- file name
- row count
- column count
- detected delimiter if available
- data quality score or warning status
- recommended workspace route

### 2. Suggested Mapping Table
Each row should show:
- source column name
- sample values
- inferred semantic role
- confidence level
- required/optional status
- user-selected final mapping
- warning messages

### 3. Missing Role Panel
Shows roles that are required for the selected workspace but not confidently mapped.

### 4. Confidence and Warning Panel
Explains why mappings may be weak:
- ambiguous column name
- missing values
- mixed types
- duplicate-like fields
- unsupported units
- low semantic confidence

### 5. Confirmation Controls
Controls should include:
- confirm mapping
- save draft mapping
- reset changes
- cancel import
- continue to import only when required fields are resolved

## Governance Requirements
The interface must clearly state:
- mapping suggestions are not verified facts
- final mapping requires user confirmation
- downstream analysis remains screening unless evidence is verified
- the system does not certify data accuracy
- system confidence is not equivalent to audit assurance

## Backend Contract Preparation
Future backend endpoints may need to support:
- storing proposed mappings
- accepting confirmed mappings
- validating required roles
- returning blocking errors
- returning non-blocking warnings
- producing a mapping audit record

## Non-Goals
This milestone does not implement:
- full UI code
- database persistence
- saved mapping plans
- flexible Circular Core import
- audit trail persistence
- production auth or user roles

## Acceptance Criteria
This milestone is complete when the repo contains a clear specification for:
- user-confirmed mapping workflow
- mapping states
- screen sections
- safety wording
- required/optional role behaviour
- future backend contract direction

## Relationship to Future Milestones
- 14C defines profiler reliability risks.
- 14D defines user confirmation before import.
- 14E defines flexible Circular Core import using confirmed mappings.
- 14F defines saved mapping plans and mapping audit trail.
