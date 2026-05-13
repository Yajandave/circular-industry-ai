# Milestone 15A — Product Stability, CI and Dependency Plan

## Purpose
Define the stability, CI, dependency, and repository hygiene plan required before Circular Industry AI continues into deeper runtime implementation.

This milestone is specification-only. It does not change runtime code, dependency files, CI configuration, or deployment settings.

## Product Reason
Circular Industry AI has grown quickly from a working technical project into a broader industrial circular economy decision-support product direction.

The next risk is no longer lack of features. The next risk is unstable growth.

Before adding more backend engines or advanced UI features, the repo needs a serious stability plan covering:
- dependency control
- automated checks
- frontend test coverage
- backend regression protection
- documentation status hygiene
- branch and PR discipline
- runtime boundary clarity
- deployment readiness planning

## Core Principle
A market-payable product needs repeatability before scale.

The project should not rely on:
- manual smoke testing only
- floating frontend dependencies
- undocumented milestone status
- large files with too many responsibilities
- unclear CI coverage
- accidental direct-to-main commits
- unchecked generated artifacts
- stale README claims

## Current Stability Strengths
The project already has several positive foundations:
- FastAPI backend
- React frontend
- SQLite development database
- backend tests
- frontend build validation
- documented governance boundaries
- rules-engine authority principle
- claim-safe wording improvements
- milestone PR workflow
- foundation documentation sequence

## Current Stability Risks
The product still has important stability risks:

### 1. Dependency Drift
Frontend dependencies still using broad/latest patterns can create future breakage.

### 2. Limited Frontend Testing
Frontend stability is mostly protected by build checks and manual review, not behavioural tests.

### 3. Fast-Growing Documentation Surface
Foundation docs are useful, but README/status documents can become stale if not actively maintained.

### 4. Large Responsibility Files
Files such as App.jsx and data_profiler.py may still carry too much responsibility.

### 5. CI Coverage Gaps
Backend tests and frontend build checks are helpful, but future product-grade CI should check more contracts.

### 6. Import and Mapping Risk
The Data Profiler, mapping confirmation, flexible import, and saved-plan concepts need future regression tests before runtime implementation.

### 7. No Production Architecture Yet
The product does not yet have production auth, multi-user access, deployment environment separation, tenant scoping, or secure audit identity.

## Stabilisation Priorities

### Priority 1 — Dependency Control
Future work should:
- pin frontend dependency versions intentionally
- avoid casual latest upgrades
- review lockfile changes carefully
- document upgrade policy
- separate dependency changes from feature PRs where possible

### Priority 2 — CI Baseline
Future CI should aim to cover:
- backend tests
- frontend build
- frontend linting if introduced
- backend linting/type checks if introduced
- API contract smoke checks
- import/profiler regression tests
- documentation link/path sanity where useful

### Priority 3 — Test Expansion
Future testing should include:
- Data Profiler edge cases
- mapping validation scenarios
- flexible import blocking/warning behaviour
- saved mapping plan compatibility logic
- claim-safety wording regression checks
- recommendation-engine unchanged-boundary checks
- frontend workflow guardrail tests

### Priority 4 — Architecture Refactor Planning
Future refactor candidates:
- split data_profiler.py into smaller modules
- keep alias registries separate from processing logic
- reduce App.jsx orchestration further
- isolate workspace routing
- isolate API client contracts
- separate presentation components from workflow state
- document domain boundary contracts

### Priority 5 — Documentation Hygiene
Future documentation checks should ensure:
- README status matches actual product maturity
- milestone list is current
- market-grade language is not overstated
- unfinished engines are clearly marked as foundation/specification
- product boundaries remain clear

### Priority 6 — Release Discipline
Future release process should define:
- branch naming
- PR templates
- expected checks
- manual verification checklist
- no installer/temp files in commits
- no direct-to-main workflow
- version tagging only when meaningful

## Recommended CI Roadmap

### Stage 1 — Existing Baseline Protection
Keep:
- backend pytest
- frontend build
- manual PR file review

### Stage 2 — Stability Checks
Add or strengthen:
- frontend linting
- backend formatting/lint checks
- dependency audit awareness
- test fixtures for profiler/import edge cases

### Stage 3 — Contract Checks
Add:
- API schema smoke checks
- sample data load test
- recommendation invariants
- mapping validation invariants
- claim-safety output checks

### Stage 4 — Deployment Readiness
Only after product foundation is stronger:
- environment variable checks
- deployment build checks
- migration strategy
- auth boundary review
- logging and monitoring plan

## Dependency Policy
Future dependency work should follow:

1. Do not upgrade dependencies casually.
2. Keep dependency changes separate from feature changes when possible.
3. Review lockfile changes before commit.
4. Pin versions for reproducibility.
5. Document why any major dependency is added.
6. Avoid heavy libraries unless they strengthen the product clearly.
7. Prefer boring, maintainable dependencies over fashionable ones.

## Branch and PR Discipline
The product should use:
- one milestone per branch
- one concern per PR
- no direct commits to main
- status and diff checks before commit
- PR file review before merge
- branch delete after merge
- local main sync after merge

## Minimum Manual Pre-Commit Checklist
Before committing future milestones:

```text
git --no-pager branch --show-current
git --no-pager status --short
git --no-pager diff --stat
```

Check:
- branch is correct
- only expected files changed
- no installer scripts
- no README installer files
- no accidental duplicate docs
- no generated caches
- no environment files
- no database files

## Non-Goals
This milestone does not implement:
- dependency pinning
- CI workflow changes
- frontend tests
- backend refactors
- production deployment
- auth
- monitoring
- database migrations

## Acceptance Criteria
15A is complete when the repo contains a clear plan for:
- dependency control
- CI maturity
- test expansion
- repo hygiene
- architecture refactor priorities
- documentation status control
- branch/PR discipline
- stability-first development sequencing

## Architecture Warning
A serious product does not become market-grade by adding more screens.

It becomes market-grade when:
- behaviour is repeatable
- assumptions are documented
- tests protect important boundaries
- dependencies are controlled
- claims are safe
- failures are visible
- evidence and audit trails are respected
