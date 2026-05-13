# Milestone 15A — Stability Checklist and CI Roadmap

## Objective
Provide a practical checklist for future stability work before further feature acceleration.

## Immediate Stability Checklist

### Git Hygiene
- Confirm correct branch before every commit.
- Avoid direct commits to main.
- Delete merged milestone branches.
- Pull latest main before starting a milestone.
- Check status and diff stat before staging.
- Remove installers and temporary README files before commit.

### File Hygiene
Do not commit:
- `.env`
- virtual environments
- local databases
- cache files
- generated build folders
- installer scripts
- extracted milestone README files
- duplicate docs outside the intended directory

### Documentation Hygiene
Check:
- README does not overstate maturity
- docs distinguish implemented features from specifications
- foundation docs remain consistent with actual code
- claim-safety language remains visible
- market-grade roadmap is honest

### Dependency Hygiene
Check:
- package versions are intentional
- lockfile changes are reviewed
- dependency changes are separated where possible
- no unused large package is added
- no dependency is added only for shiny UI

## Future CI Roadmap

### Current Baseline
The current baseline should continue to include:
- backend tests
- frontend build
- manual smoke review

### Near-Term CI Improvements
Potential future CI improvements:
- run backend tests on PRs
- run frontend build on PRs
- add frontend linting
- add backend linting
- fail on obvious formatting or syntax errors
- check that test fixtures load correctly

### Mid-Term CI Improvements
Potential future checks:
- API endpoint smoke tests
- sample CSV profiler tests
- recommendation invariant tests
- mapping validation tests
- import validation tests
- claim-safety wording checks

### Later CI Improvements
Only after implementation matures:
- deployment preview checks
- auth/security smoke checks
- migration checks
- environment validation
- audit trail persistence checks
- performance smoke checks

## Product Stability Gates

### Gate 1 — Foundation Clean
Required before more major features:
- docs current
- no installer pollution
- branch workflow stable
- dependency policy defined
- profiler hardening path documented

### Gate 2 — Ingestion Reliable
Required before pilot datasets:
- profiler edge-case tests
- confirmed mapping workflow implemented
- flexible import validation implemented
- saved mapping audit design implemented or planned

### Gate 3 — Product Pilot Ready
Required before real external users:
- clear setup instructions
- stable sample data
- reliable import path
- safe wording everywhere
- visible limitations
- repeatable tests
- deployment plan

### Gate 4 — Market V1 Candidate
Required before calling product market-grade:
- auth strategy
- user/site/org scoping
- audit persistence
- deployment architecture
- supportable documentation
- realistic pilot evidence
- security and data governance review

## Recommended PR Categories
Future PRs should be labelled mentally as:

### Documentation/Specification
No runtime behaviour changes.

### Stability/Refactor
Improves structure without changing product behaviour.

### Test/CI
Improves confidence and regression protection.

### Feature Implementation
Adds runtime behaviour.

### Product Wording/Governance
Improves claim-safety and decision-support framing.

Avoid mixing these categories unless there is a clear reason.

## Refactor Priority List

### High Priority
- data_profiler.py decomposition
- mapping validation contracts
- App.jsx orchestration reduction
- frontend API contract centralisation

### Medium Priority
- shared constants for semantic roles
- domain workspace typing or schema validation
- reusable warning components
- report wording centralisation

### Later Priority
- production auth
- multi-tenant database structure
- deployment environment setup
- monitoring and logging
- formal release versioning

## Manual Release Notes Template
Future milestone PRs can use:

```text
## Summary
- What changed
- Why it matters
- What boundary it protects

## Notes
- Runtime or documentation-only
- Known limitations
- Follow-on milestone

## Checks
- Backend tests
- Frontend build
- Manual review
- Expected files only
```

## Definition of Done
This checklist is useful when it becomes the reference point for deciding whether future changes strengthen or weaken the product foundation.
