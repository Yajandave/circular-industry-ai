# Milestone 7D Acceptance Criteria

## Objective

Add material-specific circular economy playbooks so the agent gives less generic outputs and can reason differently for metals, plastics, packaging, chemicals, WEEE, organics, process water, waste heat and mineral residues.

## Acceptance criteria

- Backend exposes material playbook endpoints:
  - `GET /api/playbooks`
  - `GET /api/playbooks/summary`
  - `GET /api/playbooks/{material_family}`
  - `GET /api/export/material-playbooks.csv`
- Circular resolution plans include material-specific fields:
  - material cycle
  - core circularity question
  - intervention patterns
  - prevention/design levers
  - routes to avoid
  - evidence tests
  - red flags
  - claim controls
  - ESRS E5 mapping
  - CTI-style metrics
- Frontend includes a Material playbooks workflow tab.
- Playbooks are visible as readable cards rather than another dense table.
- LLM reasoning context can use the richer resolution plan fields while rules remain locked.
- Playbooks do not make legal, safety, carbon or verified-impact claims.

## Manual checks

1. Load sample data.
2. Run recommendations.
3. Open Resolution plans and confirm material-specific details appear.
4. Open Material playbooks and review metals, plastics, chemicals, WEEE, organics, process water and waste heat.
5. Export material playbooks CSV.
6. Generate AI reasoning for S001 and S045 and confirm Gemini uses richer material context without changing locked rules.

## Suggested commit message

```bash
git commit -m "feat: add material-specific circular economy playbooks"
```
