# Milestone 9F: Data Quality and Import Validation Hardening

## Purpose

Milestone 9F adds a data-quality layer before the product relies on uploaded or loaded material-stream data.

A market-standard decision-support product cannot simply accept a CSV and immediately act on it. It needs to tell the user whether the data is complete, consistent and suitable for screening.

## New endpoints

```text
GET  /api/data-quality/current
POST /api/data-quality/validate-csv
```

## Checks included

The data-quality report checks:

- duplicate stream IDs
- blank required values
- zero or negative monthly quantities
- negative disposal costs
- unknown hazardous status
- high contamination status
- unexpected category values
- weak supplier specificity
- material and department breakdown
- top quantity and cost streams

## Output

The report includes:

- readiness status
- readiness score
- critical issue count
- warning issue count
- info issue count
- high-risk data flags
- issue-level recommended actions
- governance note

## Product boundary

This report supports data-readiness screening. It does not verify legal waste classification, supplier capability, environmental benefit, carbon impact or financial savings.
