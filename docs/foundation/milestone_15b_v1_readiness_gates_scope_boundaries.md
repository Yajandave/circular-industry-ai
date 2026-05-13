# Milestone 15B — V1 Readiness Gates and Scope Boundaries

## Objective
Define readiness gates for moving from foundation planning into controlled implementation.

## Gate 1 — Foundation Blueprint Complete
This gate is reached when:
- 14B foundation audit is documented
- 14C profiler reliability risks are documented
- 14D user-confirmed mapping is specified
- 14E flexible import is specified
- 14F mapping audit and saved plans are specified
- 15A stability and CI plan is documented
- 15B V1 definition is documented

Passing this gate means the blueprint is clearer.
It does not mean the product is market-grade.

## Gate 2 — Ingestion Implementation Ready
Before building deeper domains, the product should implement and test:
- stronger profiler edge-case tests
- confirmed mapping screen
- mapping validation states
- flexible Circular Core import
- row-level warnings
- blocking import conditions
- saved mapping plan design or first implementation
- import audit record

## Gate 3 — Core Workflow Reliable
Before a pilot, the product should prove:
- upload/profile works on realistic datasets
- mapping confirmation prevents silent mistakes
- import does not invent missing values
- recommendation outputs remain rules-controlled
- evidence gaps are visible
- action outputs are useful and claim-safe
- manual workflow can be repeated end-to-end

## Gate 4 — Pilot Candidate
Before showing to serious external users, the product should have:
- stable setup instructions
- known limitations page
- realistic example datasets
- clean README status
- CI passing consistently
- frontend build passing
- backend tests passing
- no misleading market-grade claims
- safe report language
- basic audit trail

## Gate 5 — Market-Grade V1 Candidate
Before positioning as market-payable, the product should have:
- dependable ingestion workflow
- tested Circular Core recommendation logic
- validated mapping/import path
- audit trail for key decisions
- deployment architecture
- authentication strategy
- data governance notes
- supportable documentation
- realistic pilot feedback
- clear commercial problem statement

## V1 In-Scope

### Core
- Circular Core workflow
- Data Profiler
- user-confirmed mapping
- flexible import
- rules-based recommendation engine
- evidence gap review
- operator triage
- action/report outputs
- claim-safe language
- basic audit traceability

### Supporting Workspaces
Supporting domains may exist as controlled issue or evidence workspaces, but should not overclaim maturity.

Allowed early scope:
- ESG issue register
- EIA issue register
- claims-risk wording review
- supplier evidence request support
- GHG data readiness notes

Not allowed early scope:
- verified ESG scoring
- verified carbon accounting
- statutory EIA conclusions
- legal claim approval
- supplier compliance certification

## V1 Out-of-Scope

### Not V1
- full enterprise SaaS
- full multi-user permissions
- official compliance certification
- legal assurance
- statutory EIA assessment
- verified GHG inventory
- automated supplier compliance judgement
- external claims approval
- production billing
- marketplace integrations

## Implementation Sequence After 15B

Recommended next implementation sequence:

```text
1. Profiler edge-case test expansion
2. data_profiler.py decomposition
3. user-confirmed mapping screen backend contract
4. user-confirmed mapping UI
5. flexible Circular Core import endpoint
6. mapped import validation tests
7. saved mapping plan/audit trail first implementation
8. README/status cleanup
9. dependency pinning and CI strengthening
10. realistic pilot dataset workflow
```

This sequence is intentionally not feature-shiny. It strengthens the path to a serious product.

## Decision Rules for Future Work

### Say Yes When
A change:
- improves ingestion reliability
- improves traceability
- protects claim boundaries
- reduces architecture risk
- improves repeatable workflows
- supports operator decision-making
- makes limitations clearer

### Say No or Later When
A change:
- adds shiny dashboards before data reliability
- expands ESG/GHG/EIA claims without engines
- hides warnings
- relies on AI to make locked decisions
- creates untested complexity
- makes README sound more mature than the product is
- mixes many concerns into one PR

## Product Positioning Boundary
Acceptable positioning:

```text
Circular Industry AI is an industrial circular economy decision-support system that helps profile operational stream data, identify circular opportunity candidates, review evidence gaps, and produce controlled action outputs.
```

Unsafe positioning:

```text
Circular Industry AI verifies carbon savings, certifies supplier compliance, proves waste diversion, or performs statutory environmental assessment.
```

## Definition of Done
15B is complete when future work can be judged against clear gates:
- foundation blueprint
- ingestion readiness
- core workflow reliability
- pilot candidacy
- market-grade V1 candidacy

The result should make the next coding phase stricter, not easier.
