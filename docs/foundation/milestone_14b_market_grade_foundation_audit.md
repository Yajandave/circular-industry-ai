# Milestone 14B - Market-Grade Foundation Audit and Stabilisation Plan

## Purpose

This milestone deliberately does not add shiny product features. It defines the foundation work required before Circular Industry AI can credibly move toward a market-payable industrial circular economy decision-support product.

Circular Core remains the primary system. ESG, GHG & Net Zero, EIA, Greenwashing / Claims, Supplier & Procurement and Data Profiler are supporting domains that must strengthen Circular Core rather than reposition the product as a generic sustainability dashboard.

## Governance boundary

The rules engine remains the locked decision source. AI/LLM may explain, summarise, classify, draft and support investigation, but it must not override:

- risk level
- review status
- rule applied
- claim boundary
- evidence controls
- legal/compliance status
- verified impact
- verified savings
- verified carbon reduction
- verified supplier compliance
- verified ESG performance
- statutory EIA significance

Dashboard and report values are screening outputs only. They are not verified savings, verified diversion, verified environmental benefit, supplier compliance confirmation or externally validated sustainability claims.

## Current audit position

The product direction is strong, but the repo has accumulated complexity quickly. The next phase should stabilise foundations before adding new domain engines or high-visibility features.

### Strengths

- Clear industrial circular economy decision-support identity.
- Backend-first rule-controlled architecture.
- Meaningful circular workflow rather than a generic dashboard.
- Evidence register, traceability, knowledge retrieval and operator workflow layers already exist.
- Data Profiler introduces an important entry point for messy real-world datasets.
- Recent wording cleanup reduces claim-safety risk.

### Risks

- Many layers have been added faster than the architecture has been consolidated.
- Some domains are visible in the workspace architecture before their backend engines are mature.
- Data Profiler is strategically important but still young.
- Important profiler logic may be concentrated in one file.
- App.jsx has improved but still has too much orchestration responsibility.
- README/status documentation may lag behind the actual repo state.
- Frontend dependencies may still be too loose for a stability phase.
- Frontend testing appears weaker than backend testing.
- Production deployment, authentication, tenancy and user-management architecture are not yet defined.

## Stabilisation priorities

### Priority 1 - Product truth and scope control

Define what the product currently does, what it does not yet do, and what must not be claimed. This should be reflected consistently across README, UI wording, report wording and domain workspaces.

Expected outcome: no part of the product implies verified savings, verified diversion, verified carbon reduction, legal compliance, supplier compliance or statutory EIA conclusions without the correct evidence controls.

### Priority 2 - Data Profiler reliability path

The Data Profiler is becoming a critical product intake layer. It needs edge-case testing, clearer semantic-role confidence logic, safer missing-role reporting and a route toward user-confirmed mapping before it should be treated as reliable for real operators.

Expected outcome: profiler outputs are treated as suggestions until confirmed by a user.

### Priority 3 - Flexible Circular Core import path

Circular Core currently depends on the product receiving data in a usable structure. Market-grade usefulness requires messy customer CSVs to be profiled, mapped, validated and imported with auditability.

Expected outcome: flexible import workflow is designed before implementation.

### Priority 4 - Traceable mapping and audit trail

If a user confirms column mappings, the product should remember what was mapped, why it was accepted, which file/run it applied to, and what warnings remained.

Expected outcome: future mapping plans and import audit logs can be implemented without inventing governance later.

### Priority 5 - Stability, CI and dependency discipline

Before the product grows further, lock down test expectations, dependency rules, frontend checks and README status.

Expected outcome: future milestones are harder to break silently.

## Architecture challenge

Do not build full ESG, GHG, EIA or Claims engines yet. They should remain structured supporting workspaces until Circular Core import, data quality, traceability and stability are stronger.

A serious product must first answer:

1. Can messy industrial data enter the system safely?
2. Can the system explain what it inferred versus what the user confirmed?
3. Can it keep claims within evidence boundaries?
4. Can a future auditor understand how a recommendation was produced?
5. Can the repo accept changes without silent regression?

If these answers are weak, more features will make the product look bigger but less trustworthy.

## Milestone sequence after 14B

- 14C - Data Profiler Reliability and Edge-Case Hardening Plan
- 14D - User-Confirmed Mapping Screen Specification
- 14E - Flexible Circular Core Import Specification
- 14F - Mapping Audit Trail and Saved Mapping Plans Specification
- 15A - Product Stability, CI and Dependency Plan
- 15B - Market-Grade V1 Definition

## Definition of done for 14B

This milestone is complete when the repo contains a clear foundation audit document that:

- confirms the product identity
- preserves the governance boundary
- names current risks without pretending they are solved
- defines the stabilisation priorities
- blocks premature shiny-feature expansion
- creates a safe bridge into 14C through 15B
