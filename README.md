# Circular Industry AI

**Working title:** Circular Industry AI: Material Flow, By-Product Valorisation and Circular Procurement Decision Support

## Project purpose

Circular Industry AI is an industry-facing portfolio project for industrial circular economy analysis. The goal is to build a structured decision-support system that can take industrial material and waste stream data, classify circular economy opportunities, flag evidence gaps, and prepare dashboard-ready recommendations for human review.

This project is designed for junior sustainability, ESG, procurement sustainability, circular economy, environmental consulting, resource efficiency and industrial sustainability roles.

## Why this is not a chatbot

This project is not intended to be a conversational circular economy assistant. A chatbot that explains circular economy concepts would be too generic and would not prove practical industrial capability.

Instead, Circular Industry AI is designed as a structured analytical workflow:

```text
CSV dataset
→ data validation
→ material/waste stream classification
→ rules-based circular economy screening
→ risk and evidence scoring
→ human-review flags
→ dashboard-ready recommendations
→ exportable evidence register
```

The future AI layer should support explanation and evidence-gap wording, but it should not make uncontrolled environmental, compliance or procurement decisions.

## Industrial circular economy relevance

Industrial circular economy is about keeping materials, components, by-products and resources in productive use for as long as possible. In an industrial setting, this means looking beyond recycling and considering material reduction, process redesign, internal reuse, supplier take-back, closed-loop recycling, by-product valorisation, industrial symbiosis, recovery and compliant disposal only where higher-value options are not viable.

This project focuses on practical industrial questions such as:

- Which material streams are high-volume or high-cost?
- Which streams could be reduced at source?
- Which supplier-linked streams could use take-back or returnable packaging?
- Which by-products could be reviewed for industrial symbiosis?
- Which streams require human review because of hazardous status, contamination or weak evidence?
- Which data gaps stop a confident circular economy recommendation?

## Milestone 1 scope

Milestone 1 creates the project foundation only. It does not include backend logic, frontend screens, the rules engine or the AI reasoning layer yet.

Included in this milestone:

- Clean repository structure for a future React + FastAPI + SQLite build
- Synthetic industrial material/waste stream dataset
- Data dictionary
- Initial project README
- Acceptance criteria
- Suggested GitHub commit message

## Repository structure

```text
circular-industry-ai/
├── README.md
├── .gitignore
├── data/
│   ├── sample_industrial_streams.csv
│   └── data_dictionary.md
├── backend/
│   ├── README.md
│   ├── app/
│   │   └── .gitkeep
│   └── tests/
│       └── .gitkeep
├── frontend/
│   ├── README.md
│   └── src/
│       └── .gitkeep
├── docs/
│   └── milestone_1_acceptance.md
└── portfolio/
    └── .gitkeep
```

## Dataset summary

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

The dataset intentionally includes variation for future rule testing, including:

- low-risk recycling opportunities
- supplier take-back opportunities
- possible closed-loop recycling cases
- internal reuse examples
- industrial symbiosis candidates
- recovery routes
- high-risk hazardous streams
- weak evidence cases requiring review
- streams where reduction is more appropriate than recycling

## Core dataset fields

The sample CSV includes:

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

## Future milestones

Planned next milestones:

1. Backend database and API
2. Rules-based circular recommendation engine
3. Risk, evidence and confidence scoring
4. AI-assisted explanation and evidence-gap layer
5. React upload and recommendation table
6. Dashboard and filters
7. Evidence register and export
8. Portfolio case study and final README

## Milestone 1 acceptance criteria

- [x] Repository structure created for React + FastAPI + SQLite project
- [x] Synthetic CSV dataset created with at least 40 industrial streams
- [x] Dataset includes all required material categories
- [x] Dataset includes all required circular economy fields
- [x] Dataset includes enough variation for future recommendation rules
- [x] README explains project purpose and why this is not a chatbot
- [x] Data dictionary explains each dataset column

## Suggested GitHub commit message

```text
chore: initialise project structure and industrial stream dataset
```

## Portfolio positioning

This milestone proves the project is being built from a realistic industrial data foundation rather than from a generic AI-chatbot idea. It shows the ability to structure circular economy data around material flows, supplier relationships, waste routes, risk conditions and evidence gaps.

---

## Milestone 2: Backend Database and API

Milestone 2 adds a working FastAPI + SQLite backend foundation.

The backend can load the synthetic industrial stream dataset into SQLite and expose it through structured API endpoints.

### Endpoints

```text
GET  /health
POST /api/streams/load-sample
GET  /api/streams
GET  /api/streams/summary
GET  /api/streams/{stream_id}
```

### What this proves

This milestone shows that the project is moving from a static dataset into a usable analytical system. The backend now provides the data layer needed for the future rules engine, scoring workflow, dashboard and evidence register.

### Suggested commit message

```text
feat: add FastAPI backend and industrial stream database
```


---

## Milestone 3: Rules-Based Circular Recommendation Engine

Milestone 3 adds the first decision-support layer. The backend can now run a deterministic rules engine over the loaded industrial streams and create circular economy recommendations.

### New recommendation endpoints

```text
POST /api/recommendations/run
GET  /api/recommendations
GET  /api/recommendations/summary
GET  /api/recommendations/{stream_id}
```

### What the rules engine produces

Each stream receives:

- recommended circular action
- circular strategy category
- reasoning
- risk level
- confidence score
- evidence quality score
- missing data
- human review flag
- estimated annual waste diversion
- estimated annual disposal cost avoided
- supplier/procurement action
- industrial symbiosis opportunity flag
- next action
- dashboard priority
- rule applied

### Example

For `S001`, Aluminium machining offcuts, the rules engine classifies the stream as a closed-loop recycling review case. The system also flags that alloy grade or material segregation evidence is needed before making a stronger circularity claim.

### What this proves

This milestone shows circular economy decision logic, not uncontrolled AI generation. It demonstrates the ability to structure industrial sustainability recommendations around material type, contamination risk, hazardous status, supplier evidence and evidence gaps.

### Suggested commit message

```text
feat: add rules-based circular recommendation engine
```


## Milestone 4 update: controlled agentic decision support

The project now includes an advanced agentic review layer. This does not turn the project into a chatbot. Instead, it creates a controlled multi-agent decision-support workflow around the rules engine.

Specialist reviewers now provide:

- evidence audit
- risk review
- procurement review
- industrial symbiosis screening
- resource efficiency review
- executive synthesis
- ranked action planning

The rules engine remains locked as the decision source. The agentic layer explains, challenges, structures and prioritises the recommendation. It cannot lower risk, remove human-review flags or verify unsupported claims.

New endpoints:

```text
GET /api/agent/review-pack/{stream_id}
GET /api/agent/management-summary
GET /api/agent/action-plan
```

## Milestone 5: Frontend recommendation review layer

Milestone 5 adds the first usable React interface for Circular Industry AI.

The interface allows a user to:

- check whether the FastAPI backend is connected
- load the sample industrial stream dataset
- upload a custom CSV that follows the data dictionary
- run the rules-based recommendation engine
- view industrial material streams
- view circular recommendations with risk, confidence, evidence and human-review badges
- open a controlled agentic review pack for an individual stream
- view a ranked action plan

The frontend is intentionally clean for the user, but the underlying system remains controlled and auditable. The browser interface does not make circular economy decisions. It displays the locked rules-engine recommendations and the agentic evidence, procurement, symbiosis and management-review context generated by the backend.

### Running the full local app

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


## Current build status

- Milestone 1: project setup and synthetic industrial dataset — complete.
- Milestone 2: FastAPI backend, SQLite database and stream API — complete.
- Milestone 3: rules-based circular recommendation engine — complete.
- Milestone 4: controlled agentic decision-support layer — complete.
- Milestone 5: React frontend recommendation review interface — complete.
- Milestone 6: dashboard and advanced recommendation filters — complete.
- Milestone 6B: UI polish and portfolio screenshot readiness — complete.
- Milestone 6C: workflow layout, progressive disclosure and domain-specific review wording — complete.
- Milestone 7: evidence register and export workflow — complete.


## Milestone 6 dashboard features

The frontend now includes a decision dashboard with strategy, risk, priority and material-quantity breakdowns. Users can search and filter by material, circular strategy, risk level, human-review status, priority band, confidence and evidence quality. Recommendations can also be sorted by priority score, annual cost exposure, diversion potential, risk severity, confidence or evidence maturity.

The dashboard is a prioritisation and screening layer only. It does not override the rules engine and does not convert estimated values into verified savings or verified environmental impact.


## Milestone 6B: UI polish and portfolio screenshot readiness

Milestone 6B improves the presentation layer after reviewing a browser/PDF export of the Milestone 6 interface.

The update adds:

- a portfolio snapshot section for recruiter-ready screenshots
- a cleaner recommendation table with fewer columns and better wrapping
- clearer priority, risk, evidence and screened-exposure grouping
- print/PDF-specific styling that hides interactive controls and large raw tables
- improved spacing to avoid clipped labels in exported views
- a stronger governance note for screening estimates versus verified impact

This milestone does not change the rules engine, scoring method or agentic controls. It only improves usability and presentation so the advanced decision-support workflow is easier for a non-technical user to understand.

### Suggested commit message

```text
style: polish dashboard UI for portfolio screenshots
```


## Milestone 6C: Workflow layout and domain-specific review polish

Milestone 6C improves the usability of the frontend without changing the locked rules engine. The interface now uses a staged workflow so users do not have to read the dashboard, recommendations, review pack, action plan and raw data all at once.

### Workflow views

1. **Executive dashboard** — summary metrics, strategy mix, risk profile, priority bands and portfolio snapshot.
2. **Recommendations** — filterable and ranked rules-engine outputs.
3. **Review pack** — selected stream drill-down covering evidence, risk, procurement, symbiosis and resource-efficiency context.
4. **Action plan** — ranked validation and opportunity-development phases.
5. **Raw data** — underlying industrial stream table, hidden by default.

### Domain-specific review wording

The agentic review layer now avoids applying generic scrap-reduction language to every stream. It includes more appropriate review prompts for grease trap waste, process water, waste heat, chemical residues, batteries, electronics, returnable containers and controlled textile/PPE-type streams.

This keeps the user experience cleaner while making the review packs more credible for industrial circular economy, EHS and procurement contexts.


## Milestone 7: Evidence register and export workflow

Milestone 7 adds an auditable evidence register and CSV export workflow. The register separates measured data, estimated calculations, assumptions, missing evidence, review gates and claim boundaries for each recommendation. This strengthens the project as an evidence-led circular economy decision-support tool rather than a generic AI dashboard.

New outputs include:

- evidence register API endpoint
- evidence maturity summary
- recommendations CSV export
- evidence register CSV export
- frontend Evidence Register workflow tab
- claim-readiness and anti-greenwashing controls

## Milestone 7B: Circular Resolution Engine

Milestone 7B adds the domain intelligence layer that turns broad rules-engine recommendations into specific circular economy intervention plans. The engine uses material-specific playbooks to produce practical resolution plans with circular problem framing, value-retention logic, implementation steps, supplier/procurement actions, process redesign actions, industrial symbiosis screening, pilot plans, KPIs, evidence requirements, decision gates, claim boundaries and fallback routes.

The rules engine remains the locked decision source. Resolution plans do not lower risk, remove human-review flags or verify claims. They support screening, pilot design and evidence-led human review.

New API endpoints:

```text
POST /api/resolutions/run
GET  /api/resolutions
GET  /api/resolutions/summary
GET  /api/resolutions/{stream_id}
GET  /api/export/resolution-plans.csv
```

Frontend workflow addition:

```text
Resolution plans
```

This milestone makes the project more clearly circular economy focused by moving beyond waste-route classification into prevention, value retention, supplier loops, process redesign, by-product valorisation, pilot planning and claim-readiness control.
