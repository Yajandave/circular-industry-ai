# 10-minute governance demonstration (external professional review)

## Purpose and limitations

Use the demo to invite critical feedback on a **controlled circular-economy screening alpha**, not to claim an independently validated or commercially deployed AI product.

This walkthrough uses **synthetic industrial streams**, an isolated SQLite demo database and **ruleset v1.0.0**. No fake external reviewer results or fictitious measured outcomes are preloaded.

## Prepare a clean dataset without deleting anything

From the repository in VS Code, run in a backend terminal:

```powershell
cd backend
.venv\Scripts\activate
python scripts/prepare_governance_demo.py
```

The script creates a **new uniquely named database** under `backend/demo_databases/` and prints the exact PowerShell `$env:DATABASE_URL = "..."` command. Copy that printed setting into the same terminal, then start the API:

```powershell
uvicorn app.main:app --reload --port 8000
```

In a second terminal:

```powershell
cd frontend
npm run dev
```

Open `http://localhost:5173`. Confirm the backend is connected. The demo has 50 synthetic streams and generated recommendations. **Do not click Load sample or Run recommendations unless demonstrating those explicit controls**; either action will operate only on this isolated demo database.

The normal, previous application database is not overwritten or reset.

## Live 10-minute navigation

| Time | Screen and record | Point to communicate |
| --- | --- | --- |
| 0:00–1:00 | Dashboard: 50 *synthetic* streams | This is screening input, not achieved diversion or savings |
| 1:00–3:00 | Recommendations → S001 aluminium machining offcuts → Open review pack | Locked metal route, risk position and specific evidence gaps; alloy grade/recycler acceptance still need proof |
| 3:00–4:30 | S001 Rule provenance + reviewer competence + ruleset version | Internal operational rule with public waste-hierarchy context, not legal certification; versioned snapshot is traceable |
| 4:30–6:00 | Recommendations → S022 spent acetone solvent → Open review pack | Hazardous solvent with human EHS/waste-classification review required; take-back cannot overrule safety |
| 6:00–7:30 | Scenario screening → S001 → Run scenario | Explicit assumptions yield a *screened* quantity only. Not verified diversion or cost savings |
| 7:30–8:30 | Evidence register and claim boundary | Observed records and internal document review are separate from external assurance |
| 8:30–9:30 | S001 Review pack → Record professional disagreement (discuss concept, do not submit fake expert view) | A challenge preserves the original locked recommendation; no automatic override |
| 9:30–10:00 | Separate tab: `/?mode=blind-review` | Ten cases, system answers hidden until actual submission; external review still pending |

If time is short, prioritise **S001 + S022 + rule provenance + claim boundary** over a lengthy feature tour.

## During the meeting

- Do **not** use the current Deepa meeting to complete the full ten-case blind review.
- Do **not** submit any statement pretending to be Deepa or another external practitioner.
- Do **not** describe 20/20 internal reference cases and 10/10 grounded challenge cases as measured real-world accuracy.
- Explain that the audit log is an alpha trace, not tamper-proof external assurance.
- Explain that reviewer identity is self-declared and there is no role-based authentication or approval authority yet.
- Leave ESG, GHG, EIA and general green-claims analytical workspaces out of the demo; those engines are not complete.

## Questions for the expert reviewer

1. Which part of the decision governance would stop you trusting this system?
2. Where is reviewer competence or second-line review insufficiently specified?
3. Is the claim boundary between screening, observation, internal review and external verification clear?
4. What should govern professional challenges and future overrides?
5. How should rule/provenance revisions be documented before independent review?

## After the call

Capture feedback verbatim as input for a future ruleset change proposal. Do **not** silently change v1.0 outputs or treat an individual's opinion as certified accuracy.

Current versioned ruleset metadata: `GET /api/recommendations/ruleset`.
Versioned history for a stream: `GET /api/recommendations/history/S001`.

Older records with no versioned snapshot remain unversioned.
