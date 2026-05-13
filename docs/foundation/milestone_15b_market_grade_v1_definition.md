# Milestone 15B — Market-Grade V1 Definition

## Purpose
Define what a credible Market-Grade V1 of Circular Industry AI should mean.

This milestone is specification-only. It does not claim the product is market-grade now. It defines the threshold the product must reach before it can honestly be positioned as a serious pilot-ready or market-payable industrial circular economy decision-support product.

## Product Identity
Circular Industry AI is:

**Industrial Circular Economy Decision Support**

The main product is Circular Core.

Supporting domains such as ESG, GHG & Net Zero, EIA, Greenwashing / Claims, Supplier & Procurement, and Data Profiler should strengthen Circular Core. They should not turn the product into a generic sustainability dashboard.

## Core Market-Grade Principle
Market-grade does not mean:
- more screens
- more AI summaries
- more dashboards
- more broad sustainability labels
- more unsupported ESG/GHG/EIA claims

Market-grade means:
- reliable ingestion
- controlled decisions
- repeatable workflows
- transparent limitations
- auditability
- evidence boundaries
- safe language
- useful outputs for real operational decisions

## What V1 Should Be
A credible V1 should focus on one strong core workflow:

```text
Industrial stream data
→ profiling
→ user-confirmed mapping
→ controlled import
→ rules-based circular recommendation
→ evidence and data-quality review
→ operator triage
→ action/report outputs
→ audit trail
```

The V1 should be narrow enough to be reliable and serious, but strong enough that an organisation could understand its value.

## V1 Must-Have Capabilities

### 1. Reliable Data Intake
The product should support:
- CSV profiling
- semantic role detection
- missing field reporting
- edge-case warnings
- data quality feedback
- user-confirmed mappings
- controlled import into Circular Core

### 2. Circular Core Decision Logic
The product should provide:
- locked rules-based recommendations
- risk levels
- review status
- claim boundaries
- evidence quality indicators
- recommendation explanations
- human review routing

### 3. Evidence and Audit Control
The product should track:
- source data limitations
- mapping decisions
- import warnings
- recommendation reasoning
- evidence gaps
- operator-facing warnings
- analysis run context

### 4. Operator Workflow
The product should help users:
- identify high-risk streams
- identify circular opportunity candidates
- understand what evidence is missing
- prioritise next actions
- prepare supplier evidence requests
- produce controlled action reports

### 5. Claim-Safe Output Language
The product must clearly avoid implying:
- verified savings
- verified diversion
- verified carbon reduction
- verified environmental benefit
- verified supplier compliance
- verified ESG performance
- statutory EIA significance

unless external verification exists and the product has a proper evidence model supporting that claim.

## V1 Should Not Try To Be
V1 should not claim to be:
- a full ESG reporting platform
- a full carbon accounting system
- a statutory EIA assessment tool
- a supplier compliance certification platform
- a legal compliance engine
- an autonomous sustainability consultant
- a verified environmental impact calculator

These may become future domains or integrations, but not before Circular Core is stable.

## V1 User Personas

### Primary User
Operations, sustainability, procurement, or facilities professional who needs to review industrial material, waste, by-product, or resource streams.

### Secondary User
Consultant or analyst supporting circular economy opportunity screening, supplier engagement, or evidence preparation.

### Future User
Multi-site organisation needing repeatable circular economy review workflows across sites or suppliers.

## V1 Workflow Definition

### Step 1 — Upload and Profile
User uploads a CSV or sample dataset.

System:
- profiles structure
- detects likely fields
- reports missing roles
- flags data quality concerns
- recommends workspace route

### Step 2 — Confirm Mapping
User reviews field mapping.

System:
- shows proposed mappings
- shows confidence and warnings
- blocks unresolved required roles
- records confirmation decision in future implementation

### Step 3 — Import into Circular Core
System imports only after required roles are resolved.

System:
- preserves raw values
- normalises where rules exist
- records warnings
- rejects or flags problematic rows

### Step 4 — Generate Circular Recommendations
Rules engine generates controlled recommendations.

System:
- does not allow AI to override rules
- keeps risk/review status locked
- separates screening from verified impact

### Step 5 — Review Evidence and Risks
User sees:
- evidence gaps
- risk flags
- supplier/procurement signals
- claim boundaries
- recommendation confidence

### Step 6 — Decide Next Action
User can produce:
- action report
- supplier evidence request
- triage summary
- management summary
- exportable evidence/action register in future versions

## V1 Quality Bar
A credible V1 should meet these quality conditions:

### Reliability
- important workflows do not break under normal use
- imports handle reasonable real-world data variation
- errors are visible and understandable
- system does not silently invent missing data

### Traceability
- analysis run context is recorded
- mapping/import decisions are traceable
- recommendation logic is explainable
- evidence gaps are visible

### Governance
- LLM remains advisory only
- rules engine remains decision source
- claim-safety language is consistent
- limitations are explicit

### Maintainability
- major files are not overloaded
- domain contracts are clear
- tests protect core logic
- dependencies are controlled

### Usability
- user understands what to do next
- warnings are not hidden
- dashboards support decisions, not decoration
- workflow order makes sense

## Market-Payable Readiness Threshold
The product should not be called market-payable until at least:

- ingestion is reliable for realistic CSVs
- confirmed mapping workflow exists
- flexible import validation exists
- core recommendations are tested
- warning and blocking states work
- evidence and claim boundaries are visible
- reports do not overclaim
- setup is repeatable
- CI checks pass consistently
- README describes maturity honestly
- pilot dataset examples are realistic
- user limitations are documented

## Pilot-Ready Threshold
Before a realistic pilot, the product should have:

- stable local/dev setup
- repeatable sample workflow
- realistic industrial test dataset
- clear known limitations
- import validation
- evidence gap visibility
- action report output
- safe management summary
- basic audit trail
- documented support process

## Not Yet Required for Early V1
These are important later, but not mandatory for early V1 foundation:

- full multi-tenant SaaS
- enterprise SSO
- advanced permission model
- formal certification workflow
- statutory compliance engine
- full carbon accounting
- production-grade observability
- paid billing system
- enterprise procurement integrations

## Future Expansion Domains
After Circular Core V1 stabilises, the product may expand into:

### ESG Workspace
Issue register, evidence gaps, risk flags, internal reporting preparation.

### GHG & Net Zero Workspace
Screening-level emissions relevance and data readiness, not verified carbon accounting at first.

### EIA Workspace
Environmental issue screening and evidence organisation, not statutory significance determination.

### Greenwashing / Claims Workspace
Claim-risk review and wording controls, not legal sign-off.

### Supplier & Procurement Workspace
Supplier-loop evidence, take-back opportunities, recycled-content data readiness, not compliance certification.

### Data Profiler Workspace
Data readiness, mapping, validation, and ingestion control.

## Success Metrics for V1
Useful V1 metrics may include:

- percentage of files profiled successfully
- percentage of imports blocked for valid reasons
- percentage of rows accepted with warnings
- number of evidence gaps identified
- number of high-risk streams flagged
- number of circular opportunities prioritised
- number of supplier evidence requests generated
- time from upload to reviewed action summary
- number of claim-sensitive warnings surfaced

These are product operation metrics, not verified environmental impact metrics.

## Non-Goals
This milestone does not implement:
- runtime code
- deployment
- authentication
- CI changes
- import engine
- saved mapping plans
- market launch assets
- pricing model
- sales material

## Acceptance Criteria
15B is complete when the repo contains a clear and honest definition of:
- what Market-Grade V1 means
- what the product should and should not claim
- what capabilities are must-have
- what quality bar is required
- what pilot readiness means
- what remains outside V1 scope

## Final Warning
Do not confuse ambition with maturity.

Circular Industry AI can become a serious product, but only if its first market-grade version is narrow, reliable, controlled, and evidence-safe.

The product should earn trust by showing where it is useful and where it stops.
