# Circular Industry AI

**Independent AI-supported circular economy and sustainability decision-support project**

Circular Industry AI explores how industrial operational data and publicly available sustainability information can be structured into evidence-aware, human-reviewed decision support.

The project combines my practical interest in **circular economy, resource efficiency and sustainable procurement** with independent research into wider corporate sustainability topics such as **ESG reporting, net zero, sustainability claims, greenwashing risk and environmental assessment**.

> **Scope note:** This is an independent development and learning project. I have not used the project to provide professional ESG assurance, certification or third-party verification. The system is designed to support analysis and investigation, not to replace qualified professional judgement.

---

## Project screenshots

Captured from the running project using its **50 synthetic industrial streams**. These demonstration outputs support screening and human review; they are not verified savings, environmental outcomes or professional assurance.

![Decision dashboard showing circular opportunity candidates, human-review items, evidence gaps and screened cost exposure](docs/screenshots/circular-industry-ai-dashboard.png)

*Circular opportunity screening, with evidence gaps and review requirements visible alongside estimated cost exposure.*

![Evidence inspector for a synthetic contaminated timber stream, showing missing evidence, a human-review gate and the claim boundary](docs/screenshots/circular-industry-ai-evidence.png)

*An evidence-sensitive record shows what is missing, why human review is required and which claims the output cannot support.*

![Supplier-loop actions for synthetic aluminium and packaging streams, showing procurement routes and supplier evidence questions](docs/screenshots/circular-industry-ai-supplier-loops.png)

*Circular opportunities become practical supplier questions and evidence requests for procurement review.*

---

## Why I built it

Industrial sustainability decisions often depend on fragmented information: material-flow data, supplier information, costs, environmental risks, evidence quality and corporate sustainability claims may all sit in different places.

I built Circular Industry AI to explore a practical question:

**Can AI help organise this information into a more structured, transparent and useful workflow while keeping evidence quality, human review and claim boundaries visible?**

The project therefore focuses less on creating a generic sustainability chatbot and more on building a controlled workflow around:

- circular economy and resource-efficiency opportunities
- material and waste-flow screening
- supplier and procurement actions
- evidence quality and missing-data visibility
- sustainability claim boundaries
- human review and approval gates
- decision-support outputs for operational users

---

## What the project demonstrates

Circular Industry AI currently demonstrates how raw industrial data can move through a controlled workflow:

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
→ optional rules-locked AI explanation and drafting
→ visual analytics and operator drilldown
```

The aim is to make the reasoning, evidence gaps and review requirements visible rather than allowing AI to produce unsupported sustainability conclusions.

---

## Sustainability topics researched

The project has required independent research across several sustainability areas.

### Applied project focus

These areas are closest to my existing sustainability experience and form the core of the product logic:

- circular economy
- resource efficiency
- waste prevention, reuse and recovery
- sustainable procurement and supplier engagement
- material-flow analysis
- evidence quality and operational decision support

### Wider research exposure

To develop the AI-supported features and governance boundaries, I have also researched publicly available information relating to:

- ESG and sustainability reporting
- net-zero concepts and emissions reporting
- sustainability claims and greenwashing risk
- environmental performance indicators
- environmental assessment / EIA concepts
- evidence quality, traceability and claim readiness

These are **research and learning areas within the project**, not claims of professional delivery experience in ESG assurance, net-zero consulting, green-claims verification or EIA practice.

---

## How public information is used

The project has been developed using publicly available sustainability information, including material from sources such as:

- government and regulatory guidance
- recognised sustainability frameworks and standards
- corporate sustainability and ESG disclosures
- academic and industry publications
- circular economy, waste and resource-efficiency guidance

This information has informed the system's rules, prompts, knowledge structure, test scenarios and governance controls.

The project does **not** treat publicly available information as independently verified truth. Source quality, evidence gaps and the need for human review remain part of the workflow.

---

## Evidence and claim-safety approach

One of the main design principles is that sustainability outputs should not be stronger than the evidence supporting them.

The evidence workflow distinguishes between:

- measured data
- estimates
- assumptions
- missing evidence
- review requirements
- claim boundaries

This allows the system to identify where an apparent sustainability opportunity may still require more information before a credible conclusion or external claim can be made.

### Governance boundary

The rules engine remains the locked decision source.

AI/LLM features may explain, summarise, draft and support investigation, but they must not override:

- risk level
- human-review status
- rule applied
- claim boundary
- evidence controls
- legal/compliance status
- verified impact

Dashboard values are screening outputs. They are **not** verified savings, verified diversion, verified environmental benefit, supplier compliance confirmation, formal ESG assurance or externally validated sustainability claims.

---

## Example use case

A company may have operational data showing material use, waste routes, disposal costs and supplier information, while separately making sustainability commitments around waste reduction or circularity.

Circular Industry AI can structure the operational information, screen for circular opportunities, identify missing evidence, suggest supplier or procurement questions and show where further review would be needed before stronger sustainability conclusions are drawn.

For example:

```text
Material stream identified
→ current route reviewed
→ circular alternative screened
→ evidence quality checked
→ missing information highlighted
→ supplier / procurement action suggested
→ human review required where risk or uncertainty is high
```

This is decision support, not third-party verification.

---

## Decision validation status

Milestone 20C begins a separate validation layer for the deterministic circular-economy decision engine.

The repository now includes an **internal 20-case decision benchmark** spanning hazardous streams, contamination controls, source reduction, supplier take-back, metals, packaging, plastics, organics, process water, mineral residues, glass, rubber, electronics/WEEE-like streams, batteries and low-information/default cases.

The benchmark checks four decision dimensions independently:

- rule selected
- circular strategy category
- risk level
- human-review requirement

The benchmark labels are explicitly marked as **internal reference expectations** and **benchmark draft**. Agreement with these labels is useful for regression testing and structured review, but it is **not external expert validation, regulatory approval, supplier acceptance evidence or proof of real-world feasibility**.

Endpoints:

- `GET /api/decision-validation/cases`
- `POST /api/decision-validation/run`
- `GET /api/decision-validation/summary`

The next validation stage is to challenge and replace these internal reference labels with documented domain judgement and realistic industrial cases.

Milestone 20C.2 adds a separate **externally grounded challenge suite** using current public guidance from GOV.UK, the Environment Agency, Defra and London Fire Brigade. These cases are not labelled with expected Circular Industry AI rule IDs. Instead, they define broader constraints such as whether human review is required, which risk bands are acceptable, which strategy categories are allowed or forbidden, and which safety/classification concepts must appear in the output.

The current grounded challenge set deliberately includes cases expected to expose weaknesses in the present engine, including damaged lithium batteries, unresolved WEEE classification, hazardous-residue packaging and edible food surplus. A gap in this suite is treated as a product finding to investigate, not as a CI failure to hide.

The interpretation of public guidance into software constraints remains an internal product judgement and is not legal advice, regulatory approval or independent professional assurance.

Milestone 20C.3 closes the four initially identified grounded gaps through general decision logic rather than case-specific exceptions:

- damaged battery condition now triggers high-risk human review even when structured hazardous/contamination flags are understated
- unresolved WEEE classification now gates recovery decisions until classification is completed
- packaging described with hazardous residues now blocks routine reuse and requires classification review
- edible food surplus now prioritises prevention and redistribution before recovery

Both validation layers are expected to remain green after these changes: the 20-case internal benchmark must retain full agreement, and all 10 current grounded challenge cases must satisfy their broader guidance-based constraints.

Milestone 20C.4 adds a **blind reviewer workflow** for the next validation stage. The reviewer-facing pack contains case data and a neutral decision taxonomy but withholds Circular Industry AI outputs, rules, grounded constraints, interpretations and expected answers. Reviewer judgements are stored immutably together with a snapshot of the system output generated only at submission time.

The workflow reports strategy-category, risk-level and human-review agreement separately. It does not call those metrics "accuracy" and does not claim independent expert validation unless reviewer competence, independence and blind conditions are documented outside the software.

Endpoints:

- `GET /api/decision-validation/blind-review-pack`
- `POST /api/decision-validation/blind-review-submit`
- `GET /api/decision-validation/blind-review-history`

Protocol: `docs/blind_review_protocol.md`

Milestone 20C.5 adds a standalone **reviewer portal** at:

`<frontend-base-url>/?mode=blind-review`

The portal is intentionally separate from the normal Circular Industry AI operator workspace. It presents one blind case at a time, requires all current cases before submission, supports print/PDF export of the full blind pack, and reveals reviewer-versus-system comparisons only after submission.

Reviewer mode is a UI isolation control, not an authentication boundary. Controlled studies should give reviewers only the reviewer-mode URL and separately document reviewer independence, competence and blind conditions.

Milestone 20C.6 adds a separate operator analysis workspace at `<frontend-base-url>/?mode=review-analysis`. It summarises reviewer distributions, leading consensus, pairwise reviewer agreement, system-versus-consensus comparison and system snapshot changes across review submissions. Reviewer consensus is explicitly not treated as ground truth, and single-reviewer cases are not described as inter-reviewer consensus.

---

## Current product capability

### 1. Controlled data intake and mapping

Users can profile uploaded CSV data before it enters the core workflow. The controlled intake process includes:

- structural and type profiling
- semantic role suggestions
- operator-confirmed field mapping
- required-role, duplicate-role and confidence validation
- mapped-row transformation into draft records
- row-level warnings and blocking errors
- preview and selected-row inspection
- explicit operator approval before persistence
- SQLite import with duplicate-ID protection
- import audit traceability
- a separate operator confirmation gate before recommendations run

Mapping validation confirms workflow readiness. It does not verify the truth, completeness or regulatory status of the source data.

### 2. Material-flow screening

After approved import, or after loading the sample dataset, users can manually run the locked rules engine to generate circular economy recommendations.

Each stream can receive:

- recommended circular action
- circular strategy category
- reasoning
- risk level
- qualitative decision-support band
- qualitative evidence maturity
- legacy internal confidence/evidence heuristics retained only for backwards compatibility and regression analysis
- missing data
- human-review flag
- annual material quantity screened / opportunity exposure
- annual disposal-cost exposure
- supplier/procurement action
- industrial symbiosis opportunity flag
- next action
- dashboard priority
- rule applied

### 3. Circular resolution planning

The Circular Resolution Engine translates recommendations into practical intervention plans, including:

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

### 5. Intervention scenario screening

A deterministic scenario engine separates baseline stream exposure from assumed intervention performance. Operators can screen a candidate route using explicit assumptions for:

- addressable fraction of the annual stream
- technical capture rate
- route or supplier acceptance rate
- scenario-screened recoverable quantity
- evidence requirements and review status
- claim boundaries

For example:

```text
20,000 kg annual stream
× 80% addressable
× 85% technically capturable
× 90% route acceptance
= 12,240 kg scenario-screened recoverable quantity
```

The result is a screening scenario, not measured diversion or verified recovery. Baseline disposal cost is shown as current exposure only and is not converted into claimed savings.

The Circular Core workflow includes a **Scenario screening** view where the operator selects a stream, reviews its locked recommendation, enters the three assumptions and sees the screened quantity, evidence needs, status and claim boundary in one panel.

The same view can compare three editable assumption cases side by side. The comparison reports the submitted-case range and sensitivity only; it does not rank, recommend or forecast which case will occur.

Operators can also save named scenario revisions and revisit them later. Saved revisions are immutable snapshots with lifecycle stages such as screening, pilot planned, pilot observed and measured-unverified. Lifecycle progress does not make a scenario claim-ready or verify impact.

A saved scenario revision can now receive immutable **observed outcome evidence** records with an observation period, observed recovered quantity, evidence reference and bounded verification status. The system compares the observation with a simple time-scaled version of the saved annual screening scenario and reports variance, while explicitly keeping the result non-claim-ready and non-causal.

Observed outcome records can then pass through an immutable **internal evidence verification and claim-readiness gate**. The gate checks documentary source presence, source traceability, quantity basis, observation-period basis, evidence completeness and internal review status. A passing review may support a narrow internal factual statement only; external claims remain blocked pending a separate verification process, and claims about causal impact, carbon savings, financial savings, legal compliance or verified diversion remain prohibited.

### 6. Controlled decision-intelligence workflows

The AI-supported layer includes:

- knowledge graph relationships
- controlled retrieval workflows
- AI-assisted insight generation
- insight history and traceability
- retrieval and insight quality evaluation

These features support investigation, explanation and drafting. They do not replace the locked rules engine, risk gates, evidence controls or professional judgement.

### 7. Visual analytics and operator drilldown

The dashboard includes decision-useful visuals for:

- risk vs opportunity
- material quantity Pareto analysis
- cost exposure Pareto analysis
- evidence maturity
- claim-readiness control
- supplier-loop opportunity profile
- scenario screening

The operator can move from a visual signal into the underlying records:

```text
Visual signal → selected slice → compact records → selected inspector → review pack
```

---

## Data model

The sample dataset contains **50 synthetic industrial streams** across areas including:

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

The synthetic dataset contains different conditions for testing, including low-risk recycling opportunities, supplier take-back routes, internal reuse, industrial symbiosis candidates, hazardous streams and weak-evidence cases requiring review.

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

- **Frontend:** React + Vite
- **Backend:** FastAPI
- **Database:** SQLite
- **Data handling:** CSV profiling, operator-confirmed mapping, controlled draft transformation, approval-gated import and structured API endpoints
- **AI layer:** optional rules-locked LLM explanation, drafting and research support
- **Testing:** backend pytest and frontend production build

---

## Development status

The repository currently implements the controlled local workflow through **Milestone 20C.6**, followed by a dedicated pre-external-review hardening phase covering audit integrity, qualitative evidence maturity, rule provenance, reviewer-competence routing, evidence-source governance and immutable human decision challenges.

The project remains development-stage software. Its outputs are screening and workflow records rather than externally verified environmental performance, legal conclusions or professional assurance opinions.

The current validation position is:
- internal deterministic benchmark retained across 20 reference cases
- externally grounded challenge suite retained across 10 England-focused cases
- blind reviewer workflow implemented
- multi-reviewer agreement analysis implemented
- independent external review not yet completed

<details>
<summary><strong>Technical milestone history</strong></summary>

- **Milestones 1–8F: Core screening and controlled outputs** — dataset and repository foundation; FastAPI, SQLite and stream APIs; locked circular recommendation engine; React review interface; dashboard and filters; evidence register; Circular Resolution Engine; material playbooks; supplier-loop intelligence; AI-assisted evidence explanations, supplier drafting and circular action reports.
- **Milestones 9A–9F: Alpha hardening and traceability** — workflow readiness diagnostics; bounded AI runtime handling; frontend workflow guardrails; organisation, site and analysis-run metadata; audit events; CSV data-quality validation.
- **Milestones 10A–10E: Knowledge and AI-assisted insight layer** — knowledge architecture; controlled knowledge base; retrieval engine; AI-assisted insight generation; saved insight history and traceability.
- **Milestones 11A–11E: Controlled decision-intelligence workflow** — knowledge graph relationships; controlled retrieval orchestration; retrieval and insight evaluation; operator UI; usability refinement.
- **Milestones 12A–12F: Professional intelligence interface** — visual analytics; drilldown and triage; product wording alignment; executive report generator; ESG/EIA issue register; scenario comparison.
- **Milestones 13A–13C: Workspace and claim-safety architecture** — domain workspace architecture; workspace contract hardening; metric and claim-safety wording.
- **Milestones 14A–14F: Data Profiler and ingestion design foundation** — profiler engine; foundation audit; profiler reliability plan; user-confirmed mapping specification; flexible import specification; mapping audit and saved-plan specification.
- **Milestones 15A–15B: Stability and V1 definition** — CI/dependency plan; V1 definition, readiness gates and scope boundaries.
- **Milestones 16A–16D: Data Profiler stabilisation** — edge-case tests; configuration modularisation; type-inference modularisation; semantic role-scoring modularisation.
- **Milestones 17A–17F: User-confirmed mapping** — validation contract and API; frontend API client; operator mapping panel; mapping UX hardening; role-option and copy alignment.
- **Milestones 18A–18E: Controlled draft import preview** — flexible import contract and endpoint; frontend client; draft preview panel; row inspection, grouped warnings and review-control hardening.
- **Milestones 19A–19D: Approved persistence and recommendation gate** — approval-controlled SQLite import; audit traceability; frontend save action; separate operator-triggered post-import recommendation run.
- **Milestone 20A: Decision-integrity hardening** — repaired post-import gate state; aligned controlled-import wording; reclassified annual quantity/cost values as screening exposure rather than achieved impact; blocked missing or unsupported quantity units; added field-level source provenance to draft rows and import audit metadata.
- **Milestones 20B.1–20B.6: Scenario, outcome and claim-readiness controls** — intervention scenario screening and comparison; immutable saved revisions; observed outcome evidence; deterministic internal evidence-review gate.
- **Milestones 20C.1–20C.6: Decision validation** — internal benchmark; authoritative-guidance challenge suite; rule-gap closure; blind external-review workflow; standalone reviewer portal; multi-reviewer agreement analysis.
- **Pre-external-review hardening:** audit/data integrity; qualitative governance maturity replacing score-led presentation; rule provenance; reviewer-competence routing; evidence-source hierarchy; immutable human disagreement records; public terminology cleanup.

**Current implemented stage: controlled circular-economy decision-support alpha, prepared for external blind review.**

</details>

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

## What I have learned from building it

The project has strengthened my ability to connect sustainability research with data structures, operational decision-making and evidence controls.

It has also given me a practical way to independently explore areas beyond my direct professional experience, including ESG reporting, net-zero concepts, greenwashing risk and sustainability claim credibility, while keeping a clear distinction between **research exposure** and **professional assurance or consulting experience**.

---

## Project limitations

Circular Industry AI is an independent learning and development project.

It does not provide:

- formal ESG or sustainability assurance
- certification
- legal or regulatory advice
- verified greenhouse-gas inventories
- professional EIA conclusions
- independent verification of corporate sustainability claims

Any real-world use would require appropriate primary evidence, subject-matter review, applicable standards and professional judgement.
