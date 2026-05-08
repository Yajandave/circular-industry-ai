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
