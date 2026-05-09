# Milestone 8F: Frontend Circular Action Report Panel

## Purpose

Milestone 8F makes the 8E circular action report builder visible in the React app.

It adds a new workflow tab:

```text
Action report
```

The tab lets the user select a stream and generate a consultant-style report from the backend endpoint:

```text
POST /api/reports/streams/{stream_id}/circular-action-report
```

## Report sections

The frontend displays:

- report title
- executive summary
- locked recommendation
- risk and review status
- evidence position
- circular resolution summary
- supplier-loop summary
- implementation plan
- evidence to collect
- recommended next actions
- unsafe claims to avoid
- claim boundary
- governance note

## Governance boundary

The report remains advisory only. It does not override locked data from the rules engine, evidence register, resolution plan or supplier-loop plan.

## Portfolio value

This completes a strong workflow:

```text
screen stream -> evidence register -> supplier request -> circular action report
```

The report panel is designed for portfolio screenshots, review packs and browser print-to-PDF export.
