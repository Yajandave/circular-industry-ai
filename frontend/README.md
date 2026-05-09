# Circular Industry AI Frontend

React + Vite interface for the Industrial Circular Economy AI Agent portfolio project.

## Current milestone

Milestone 7: evidence register, audit trail and export workflow.

## What the frontend does

- Connects to the FastAPI backend.
- Loads the synthetic manufacturing material-flow dataset.
- Uploads a custom CSV following the data dictionary.
- Runs the locked rules-based recommendation engine.
- Shows dashboard cards for material quantity, human review, value exposure and recommendation portfolio status.
- Displays visual breakdowns for strategy mix, risk profile, priority bands and annual material quantity by material type.
- Provides advanced filters for search, material, strategy, risk, review status, priority band, confidence and evidence score.
- Sorts recommendations by priority, annual cost exposure, diversion potential, risk, confidence or evidence maturity.
- Opens controlled agentic review packs for evidence, risk, procurement, industrial symbiosis and resource-efficiency context.
- Shows a ranked action plan while keeping the rules engine as the locked decision source.
- Provides an Evidence Register tab with missing data, review gates, claim boundaries and CSV exports.

## Run locally

```bash
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

The backend should be running at:

```text
http://127.0.0.1:8000
```

If your local npm install tries to use a private or unavailable registry, run:

```bash
npm config set registry https://registry.npmjs.org/
```

Then delete `node_modules` and `package-lock.json`, reinstall, and run the frontend again.

## Governance note

Dashboard figures are screening outputs. They should not be presented as verified savings, verified diversion or verified environmental benefit until actions are completed and evidenced.


## Milestone 6B polish

This frontend now includes a portfolio snapshot section and print-safe styling. Use the browser print dialog or screenshot tools to capture the dashboard without the full 50-row table overwhelming the output.

The screen interface still keeps the detailed recommendation and stream tables for operational review, while the print view prioritises:

- project title and governance statement
- summary metrics
- decision dashboard
- portfolio snapshot
- quick-win and controlled-review examples

This keeps the user experience simple while preserving the advanced controlled-agentic workflow underneath.


## Milestone 6C workflow polish

Milestone 6C changes the interface from one long data-heavy page into a staged decision workflow:

- Executive dashboard: portfolio summary, strategy mix, risk profile and screenshot-ready portfolio snapshot.
- Recommendations: filters, ranking and locked rules-engine recommendation table.
- Review pack: focused evidence, risk, procurement, symbiosis and resource-efficiency drill-down for a selected stream.
- Action plan: ranked validation and opportunity-development phases.
- Raw data: the underlying industrial stream dataset, now hidden from the default landing view.

The aim is industrial-grade capability with progressive disclosure: summary first, drill-down only when the user needs it.

Milestone 6C also improves domain-specific review-pack wording for streams such as grease trap waste, process water, waste heat, chemical residues, batteries, electronics and returnable containers. This avoids generic manufacturing-scrap language being applied to streams where it does not fit.


## Milestone 7 evidence workflow

The frontend now includes an Evidence Register tab. It shows evidence maturity, human-review gates, missing data, claim boundaries and export controls for recommendations and evidence-register CSV files.

## Milestone 7B UI

The frontend includes a new **Resolution plans** workflow tab. This view shows specific circular intervention plans generated from the locked recommendation run, including implementation steps, supplier/procurement actions, process redesign actions, KPIs, evidence requirements, claim boundaries and fallback routes.

Use the workflow in this order:

```text
Load sample dataset
Run recommendations
Open Resolution plans
Export resolution plans CSV
```


## Milestone 7C: Rules-locked LLM reasoning and UI QA

This milestone adds an optional LLM reasoning layer that writes stream-specific explanations, supplier questions, evidence-gap summaries and pilot guidance from locked rules, evidence and resolution-plan context. It also improves table wrapping, badge layout and page readability. The LLM cannot override risk, human-review gates, rule applied or claim boundaries. If no API key is configured, the app uses deterministic fallback reasoning.


## Gemini free-tier LLM setup

The optional Milestone 7C LLM reasoning layer can run through Gemini Developer API. Keep it off by default for safe local demos, then enable it in `backend/.env` when you have a Gemini API key:

```env
AI_REASONING_ENABLED=true
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_MODEL=gemini-2.5-flash
GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta
```

The LLM is rules-locked: it can explain, draft supplier questions and summarise evidence gaps, but it cannot change the rule, risk level, human-review flag or claim boundary.


## Milestone 7D UI

The workflow includes a **Material playbooks** tab. It shows material-specific circular economy patterns, evidence tests, red flags, pilot ideas and claim controls. This keeps the interface usable while giving the agent a stronger circular economy knowledge layer.
