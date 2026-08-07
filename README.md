# Circular Industry AI

**Professional product direction:** industrial circular economy, ESG, EIA and sustainability intelligence dashboard.

Circular Industry AI is a professional decision-support platform for industrial circular economy and sustainability intelligence. It converts raw operational material-flow data into rules-locked circular recommendations, evidence controls, supplier-loop actions, ESG/EIA-relevant risk signals, claim-readiness checks, agentic insight workflows and operator-facing analytics.

It is designed as an operator-facing intelligence system, not a generic chatbot and not a presentation-only dashboard.

## Development status

The repository currently implements the controlled local workflow through **Milestone 19D**. This includes CSV profiling, operator-confirmed mapping, draft transformation and preview, approval-gated SQLite persistence, import audit traceability, and a separate operator-triggered recommendation run.

The project remains a development-stage decision-support product. Its outputs are screening and workflow records, not externally verified environmental performance, legal conclusions or production assurance.

---

## Current product capability

Circular Industry AI supports a full screening-to-review workflow:

```text
Raw operational CSV or sample data
→ data profiling and semantic role suggestions
→ operator-confirmed field mapping
→ controlled draft transformation and preview
→ approval-gated SQLite import and audit event
→ operator-triggered rules-based circular economy screening
→ risk, confidence and evidence scoring
→ evidence register and claim controls
→ circular resolution plans
→ supplier-loop and circular procurement intelligence
→ optional rules-locked AI reasoning
→ agentic retrieval and insight workflows
→ visual analytics dashboard
→ operator drilldown and decision triage
```

The system is intended for professional circular economy, ESG, EIA, sustainability, resource-efficiency, procurement-sustainability and industrial operations contexts.

---

## Governance boundary

The rules engine remains the locked decision source.

AI/LLM features may explain, summarise, draft and support investigation, but they must not override:

- risk level
- human-review status
- rule applied
- claim boundary
- evidence controls
- legal/compliance status
- verified impact

Dashboard values are screening outputs. They support prioritisation and operator attention. They are not verified savings, verified diversion, verified environmental benefit, supplier compliance confirmation or externally validated sustainability claims.

---

## Why this is not a chatbot

Circular economy and sustainability decisions in industrial settings require controlled evidence, review gates and claim boundaries.

A free-form chatbot would be too generic and too risky for:

- waste classification and compliance-sensitive decisions
- supplier evidence requests
- ESG claim-readiness
- circular procurement routes
- EIA-style issue scoping
- human-review gates
- evidence-gap handling

Circular Industry AI is instead built as a structured analytical workflow where AI supports controlled explanation and drafting around a locked decision record.

---

## Product users

The dashboard is designed for professional users such as:

- circular economy analysts
- ESG and sustainability analysts
- EIA / environmental assessment support teams
- resource-efficiency teams
- procurement sustainability teams
- industrial operations and facilities teams
- supplier engagement and circular procurement teams

---

## Core workflows

### 1. Controlled data intake and mapping

Users can profile uploaded CSV data before it enters Circular Core. The controlled intake workflow includes:

- structural and type profiling
- semantic role suggestions
- operator-confirmed field mapping
- required-role, duplicate-role and confidence validation
- mapped-row transformation into draft Circular Core records
- row-level warnings and blocking errors
- preview and selected-row inspection
- explicit operator approval before persistence
- SQLite import with duplicate-ID protection
- import audit traceability
- a separate operator confirmation gate before recommendations run

Mapping validation confirms workflow readiness. It does not verify the truth, completeness or regulatory status of the source data.

### 2. Material-flow screening

After approved import, or after loading the sample dataset, users can manually run the locked rules engine to generate circular economy recommendations.

Each stream receives:

- recommended circular action
- circular strategy category
- reasoning
- risk level
- confidence score
- evidence quality score
- missing data
- human-review flag
- estimated annual waste diversion
- estimated annual disposal cost exposure
- supplier/procurement action
- industrial symbiosis opportunity flag
- next action
- dashboard priority
- rule applied

### 3. Evidence register and claim controls

The evidence workflow separates:

- measured data
- estimates
- assumptions
- missing evidence
- review gates
- claim boundaries

This helps prevent unsupported circularity, ESG or sustainability claims.

### 4. Circular resolution planning

The Circular Resolution Engine translates recommendations into practical circular economy intervention plans, including:

- value-retention logic
- implementation steps
- process redesign actions
- supplier/procurement actions
- industrial symbiosis screening
- pilot plans
- KPIs
- evidence requirements
- decision gates
- fallback routes

### 5. Supplier-loop and circular procurement intelligence

The supplier-loop workflow turns circular recommendations into procurement-facing actions, including:

- reverse-logistics models
- supplier questions
- contract levers
- evidence requests
- commercial checks
- operational checks
- acceptance criteria
- pilot scopes
- fallback positions

### 6. Agentic intelligence workflows

The agentic intelligence layer supports controlled investigation through:

- knowledge graph relationships
- agentic retrieval workflow
- insight generation
- insight history and traceability
- retrieval and insight quality evaluation

These workflows support investigation. They do not replace the locked rules engine.

### 7. Visual analytics and operator drilldown

The dashboard includes decision-useful visuals for:

- risk vs opportunity matrix
- material quantity Pareto
- cost exposure Pareto
- evidence maturity
- claim-readiness control
- supplier-loop opportunity profile
- scenario screening

The operator drilldown layer lets users move from a visual signal into the underlying records:

```text
Visual signal → selected slice → compact records → selected inspector → review pack
```

---

## Current milestone status

All milestones listed below are merged into `main`. Milestones 14 and 15 include architecture, reliability and V1 scope specifications as well as implementation planning; they should not be read as production-readiness claims.

- **Milestones 1–8F: Core screening and controlled outputs** — dataset and repository foundation; FastAPI, SQLite and stream APIs; locked circular recommendation engine; React review interface; dashboard and filters; evidence register; Circular Resolution Engine; material playbooks; supplier-loop intelligence; AI-assisted evidence explanations, supplier drafting and circular action reports.
- **Milestones 9A–9F: Alpha hardening and traceability** — workflow readiness diagnostics; bounded AI runtime handling; frontend workflow guardrails; organisation, site and analysis-run metadata; audit events; CSV data-quality validation.
- **Milestones 10A–10E: Knowledge and autonomous insight layer** — knowledge architecture; controlled knowledge base; retrieval engine; autonomous insight generation; saved insight history and traceability.
- **Milestones 11A–11E: Agentic intelligence workflow** — knowledge graph relationships; agentic retrieval orchestration; retrieval and insight evaluation; operator UI; usability refinement.
- **Milestones 12A–12F: Professional intelligence interface** — visual analytics; drilldown and triage; product wording alignment; executive report generator; ESG/EIA issue register; scenario comparison.
- **Milestones 13A–13C: Workspace and claim-safety architecture** — domain workspace architecture; workspace contract hardening; metric and claim-safety wording.
- **Milestones 14A–14F: Data Profiler and ingestion design foundation** — profiler engine; market-grade foundation audit; profiler reliability plan; user-confirmed mapping specification; flexible Circular Core import specification; mapping audit and saved-plan specification.
- **Milestones 15A–15B: Stability and V1 definition** — CI/dependency plan; market-grade V1 definition, readiness gates and scope boundaries.
- **Milestones 16A–16D: Data Profiler stabilisation** — edge-case tests; configuration modularisation; type-inference modularisation; semantic role-scoring modularisation.
- **Milestones 17A–17F: User-confirmed mapping** — validation contract and API; frontend API client; operator mapping panel; mapping UX hardening; role-option and copy alignment.
- **Milestones 18A–18E: Controlled draft import preview** — flexible import contract and endpoint; frontend client; draft preview panel; row inspection, grouped warnings and review-control hardening.
- **Milestones 19A–19D: Approved persistence and recommendation gate** — approval-controlled SQLite import; audit traceability; frontend save action; separate operator-triggered post-import recommendation run.

**Current implemented milestone: 19D — Post-import Recommendation Run Gate.**

---

## Local development

Start the backend:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

Start the frontend in a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

Run frontend build:

```powershell
cd frontend
npm run build
```

Run backend tests:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```

---

## Data model

The sample dataset contains 50 synthetic industrial streams across:

- metals
- plastics
- cardboard and packaging
- wood and pallets
- chemicals and solvents
- textiles
- glass
- rubber
- electronic components
- organic and process residues
- process water and energy/resource streams

The dataset includes variation for rule testing, including:

- low-risk recycling opportunities
- supplier take-back opportunities
- closed-loop recycling cases
- internal reuse examples
- industrial symbiosis candidates
- recovery routes
- high-risk hazardous streams
- weak evidence cases requiring review
- streams where reduction is more appropriate than recycling

Core fields include:

- `stream_id`
- `stream_name`
- `material`
- `source_process`
- `monthly_quantity_kg`
- `current_route`
- `disposal_cost_per_month`
- `contamination_risk`
- `hazardous_flag`
- `department`
- `supplier`
- `supplier_takeback_available`
- `recycled_content_available`
- `notes`

---

## Technology stack

- Frontend: React + Vite
- Backend: FastAPI
- Database: SQLite
- Data handling: CSV profiling, operator-confirmed mapping, controlled draft transformation, approval-gated SQLite import and structured API endpoints
- Optional AI: rules-locked LLM explanation/drafting layer
- Testing: backend pytest, frontend production build

---

## Professional positioning

Circular Industry AI is positioned as a market-relevant industrial sustainability intelligence dashboard.

It demonstrates how raw operational data can be converted into controlled, auditable and decision-useful circular economy intelligence without allowing AI to override governance-critical decision fields.

The product direction is:

```text
Industry-grade
Operator-facing
Evidence-controlled
Claim-safe
ESG/EIA-aligned
Circular procurement aware
Sustainability intelligence focused
```
