# Milestone 7B Acceptance: Circular Resolution Engine

## Objective

Add a domain-specific circular economy resolution layer that turns broad rules-engine recommendations into specific intervention plans for industrial material, waste and by-product streams.

## What changed

- Added material-specific circular economy playbooks.
- Added circular resolution plan generation.
- Added decision gates, fallback routes, KPIs and claim boundaries.
- Added backend endpoints for resolution plans and CSV export.
- Added a frontend workflow tab for resolution plans.

## New API endpoints

- `POST /api/resolutions/run`
- `GET /api/resolutions`
- `GET /api/resolutions/summary`
- `GET /api/resolutions/{stream_id}`
- `GET /api/export/resolution-plans.csv`

## Acceptance criteria

- The system generates one resolution plan per rules-engine recommendation.
- Plans preserve the locked recommendation, risk level and human-review flag.
- Hazardous or high-risk streams are not framed as circular quick wins.
- Each plan includes a specific resolution idea, implementation steps, supplier/procurement action, process redesign action, pilot plan, KPIs, evidence required, decision gates, claim boundary and fallback route.
- The frontend has a Resolution plans tab.
- Resolution plans can be exported as CSV.

## Professional value

This milestone strengthens the project from a waste-stream recommendation dashboard into a circular economy intervention-design system. It makes the output more specific, more evidence-controlled and more aligned with industrial circular economy practice.
