# Milestone 14E — Flexible Circular Core Import Specification

## Purpose
Define the flexible import behaviour required for Circular Core to accept user-confirmed mappings instead of relying on one fixed CSV schema.

This milestone is specification-only. It does not implement the import engine yet.

## Product Reason
Circular Industry AI should not require every organisation to reshape data into one rigid template before the product can be useful.

Real industrial data may come from:
- waste contractor exports
- procurement spreadsheets
- site operations logs
- supplier reports
- finance or cost trackers
- internal ESG evidence registers
- maintenance or production systems

These datasets may describe similar circular economy information using different column names, units, formats, and completeness levels.

The Data Profiler and User-Confirmed Mapping workflow prepare the input. The Flexible Circular Core Import layer must define how confirmed mappings become safe operational records.

## Core Principle
Flexible import must increase usability without weakening evidence control.

The system may accept different input schemas only when:
- required semantic roles are resolved
- user-confirmed mappings exist
- missing fields are handled explicitly
- unsupported fields are not silently interpreted
- import warnings are retained
- downstream outputs remain screening outputs

## Relationship to Previous Milestones
- 14C identifies Data Profiler reliability and edge-case risks.
- 14D defines user confirmation of system-proposed mappings.
- 14E defines how confirmed mappings should be used for Circular Core import.
- 14F will define saved mapping plans and mapping audit trail.

## Required Import Inputs
A future flexible import endpoint should receive:

### 1. Source Dataset Metadata
- file name
- upload timestamp
- row count
- column count
- delimiter if available
- profiler summary reference if available

### 2. Confirmed Mapping Object
For each imported field:
- source column name
- target semantic role
- mapping state
- user confirmation status
- confidence level from profiler
- warning list if any
- required or optional role status

### 3. Row-Level Data
The raw row values should be transformed into Circular Core-compatible structures only after mapping validation.

### 4. Import Context
- organisation if available
- site if available
- analysis run if available
- workspace route
- import mode
- operator identity in future multi-user versions

## Required Semantic Roles for Circular Core
A practical Circular Core import should eventually require or strongly prefer:

### Required Minimum Roles
- material or stream name
- current route
- quantity or volume indicator

### Strongly Recommended Roles
- monthly quantity
- unit
- department or source process
- supplier
- disposal cost
- contamination risk
- hazardous flag
- notes or evidence comments

### Optional Roles
- recycled content availability
- supplier take-back availability
- site
- organisation
- contract reference
- evidence source
- date period

The exact required set may vary by import mode, but the system must not pretend incomplete data supports full analysis.

## Import Modes
Future implementation may support:

### 1. Screening Import
Allows limited import when minimum required roles are present.
Outputs remain early screening outputs with stronger warning language.

### 2. Operational Review Import
Requires more complete fields and enables recommendation review workflows.

### 3. Evidence-Ready Import
Requires source, confidence, date period, and evidence notes before stronger reporting workflows are allowed.

## Validation Requirements
The flexible import layer should validate:

- required roles are present
- one source column is not mapped to conflicting required roles
- duplicate mappings are either blocked or explicitly resolved
- numeric fields can be parsed safely
- units are recognised or marked unsupported
- boolean fields are normalised carefully
- hazardous flags are not guessed from weak text alone
- empty rows are handled consistently
- rows with critical missing values are flagged
- row-level warnings are retained

## Transformation Requirements
Confirmed mappings should transform source data into the internal Circular Core shape.

The transformation should:
- preserve raw values where useful
- store normalised values separately
- record transformation warnings
- avoid inventing missing values
- avoid treating inferred values as verified evidence
- keep screening calculations separate from verified impact

## Import Output
A future import operation should return:

- import status
- number of rows accepted
- number of rows rejected
- number of rows accepted with warnings
- blocking errors
- non-blocking warnings
- generated analysis run ID if applicable
- mapping summary
- unresolved field summary
- row-level issue summary

## Blocking Conditions
Import should be blocked when:
- required roles are unresolved
- confirmed mapping is missing
- a required field has no usable values
- field conflicts cannot be resolved
- file cannot be parsed safely
- row structure is unstable or inconsistent

## Warning Conditions
Import may continue with warnings when:
- optional roles are missing
- units are unknown but raw values are preserved
- some rows are sparse
- confidence was low but user confirmed the mapping
- non-critical values could not be normalised
- source evidence quality is weak

## Governance Wording
The UI and reports should continue to state:
- imported data is user-provided
- mapping confirmation does not verify source accuracy
- system outputs are screening outputs unless externally verified
- values are not verified savings, verified diversion, verified carbon reduction, verified environmental benefit, or verified supplier compliance
- claim-sensitive outputs require evidence review

## Non-Goals
This milestone does not implement:
- import endpoint code
- frontend mapping screen code
- saved mapping plans
- database migrations
- production authentication
- multi-user permissions
- full ESG, GHG, EIA, or Claims engines

## Acceptance Criteria
14E is complete when the repo contains a clear specification for:
- flexible Circular Core import behaviour
- confirmed mapping as a prerequisite
- required and optional semantic role handling
- validation and transformation rules
- blocking and warning conditions
- screening-only governance language

## Architecture Warning
This layer must not become a generic CSV importer that dumps arbitrary spreadsheet data into the product.

It must remain tied to the main product identity:

**Industrial Circular Economy Decision Support**

Flexible import exists to strengthen Circular Core, not to turn the system into a generic data dashboard.
