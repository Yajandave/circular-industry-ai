# Milestone 1 Acceptance Criteria

## Objective

Set up the project foundation and create a realistic synthetic industrial material/waste stream dataset.

## Completed items

- Repository structure created for a future React + FastAPI + SQLite project.
- Synthetic CSV dataset created with 50 industrial material/waste/resource streams.
- Dataset includes required material categories:
  - metals
  - plastics
  - cardboard/packaging
  - wood/pallets
  - chemicals/solvents
  - textiles
  - glass
  - rubber
  - electronic components
  - organic/process residue
- Dataset includes required fields:
  - stream_name
  - material
  - source_process
  - monthly_quantity_kg
  - current_route
  - disposal_cost_per_month
  - contamination_risk
  - hazardous_flag
  - department
  - supplier
  - supplier_takeback_available
  - recycled_content_available
  - notes
- Dataset includes variation for later recommendation logic:
  - reduce
  - internal reuse
  - supplier take-back
  - closed-loop recycling
  - open-loop recycling
  - industrial symbiosis
  - recovery
  - compliant disposal
  - human review required
- README explains project purpose, industrial circular economy relevance, and why this is not a chatbot.
- Data dictionary explains all columns.

## Manual checks

1. Open `data/sample_industrial_streams.csv` and confirm it has 50 data rows.
2. Confirm all required columns are present.
3. Confirm hazardous and unknown-status streams exist for future human-review rules.
4. Confirm low-risk, supplier-linked and high-volume streams exist for future circular opportunity rules.

## Suggested GitHub commit message

```text
chore: initialise project structure and industrial stream dataset
```
