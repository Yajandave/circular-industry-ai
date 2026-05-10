# Circular Industry AI

**Professional product direction:** industrial circular economy, ESG, EIA and sustainability intelligence dashboard.

Circular Industry AI is a professional decision-support platform for industrial circular economy and sustainability intelligence. It converts raw operational material-flow data into rules-locked circular recommendations, evidence controls, supplier-loop actions, ESG/EIA-relevant risk signals, claim-readiness checks, agentic insight workflows and operator-facing analytics.

It is designed as an operator-facing intelligence system, not a generic chatbot and not a presentation-only dashboard.

---

## Current product capability

Circular Industry AI supports a full screening-to-review workflow:

```text
Raw operational data
→ material and waste stream database
→ rules-based circular economy screening
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

### 1. Material-flow screening

Users can load or upload industrial material and waste stream data, then run the locked rules engine to generate circular economy recommendations.

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

### 2. Evidence register and claim controls

The evidence workflow separates:

- measured data
- estimates
- assumptions
- missing evidence
- review gates
- claim boundaries

This helps prevent unsupported circularity, ESG or sustainability claims.

### 3. Circular resolution planning

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

### 4. Supplier-loop and circular procurement intelligence

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

### 5. Agentic intelligence workflows

The agentic intelligence layer supports controlled investigation through:

- knowledge graph relationships
- agentic retrieval workflow
- insight generation
- insight history and traceability
- retrieval and insight quality evaluation

These workflows support investigation. They do not replace the locked rules engine.

### 6. Visual analytics and operator drilldown

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

- Milestone 1: repository setup and industrial stream dataset — complete
- Milestone 2: FastAPI backend, SQLite database and stream API — complete
- Milestone 3: rules-based circular recommendation engine — complete
- Milestone 4: controlled agentic decision-support layer — complete
- Milestone 5: React frontend recommendation review interface — complete
- Milestone 6: dashboard and advanced recommendation filters — complete
- Milestone 6B: interface polish and management-summary view — complete
- Milestone 6C: workflow layout, progressive disclosure and domain-specific review wording — complete
- Milestone 7: evidence register and export workflow — complete
- Milestone 7B: Circular Resolution Engine — complete
- Milestone 7C: rules-locked optional LLM reasoning — complete
- Milestone 7D: material-specific circular playbooks — complete
- Milestone 7E: circular procurement and supplier-loop intelligence — complete
- Milestone 8E: circular action report builder — complete
- Milestone 10D: Autonomous Insight Generator — complete
- Milestone 10E: Insight History and Traceability — complete
- Milestone 11A: Knowledge Graph Relationship Layer — complete
- Milestone 11B: Agentic Retrieval Workflow — complete
- Milestone 11C: Retrieval and Insight Quality Evaluation — complete
- Milestone 11D: Operator UI for Agentic Intelligence — complete
- Milestone 11E: Operator UI Usability Refinement — complete
- Milestone 12A: Visual Analytics Dashboard — complete
- Milestone 12B: Operator Drilldown and Decision Triage Layer — complete
- Milestone 12C: Professional Product Wording Alignment — current

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
- Data handling: CSV ingest and structured API endpoints
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
