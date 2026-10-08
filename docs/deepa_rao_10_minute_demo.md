# Deepa Rao — 10-minute Circular Industry AI demonstration

**Purpose:** Invite a critical governance review of a circular-economy decision-support alpha. This is a demonstration of **controls**, not a pitch, product assurance or request for endorsement.

**Environment:** Local frontend + local FastAPI backend with a **fresh, disposable synthetic-data SQLite database**. Do not show real supplier data, previously created test submissions, external reviewer names or private API keys.

## Run it locally on Windows (PowerShell)

Open **Terminal 1** in the repository:

```powershell
cd backend
python -m pip install -r requirements.txt
$env:DATABASE_URL = 'sqlite:///./deepa_review_demo_fresh.db'
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Use a **new file name** for each rehearsal if one already exists. Do not delete or overwrite an existing SQLite database to create a clean demo. The FastAPI startup creates tables in the new file automatically.

Open **Terminal 2**, from the repository root:

```powershell
cd frontend
npm ci
npm run dev -- --host 127.0.0.1
```

Open **http://127.0.0.1:5173/**. The API health check is **http://127.0.0.1:8000/health**.

> The browser automation in CI uses its own disposable database; those test reviewers and challenges are not external validation. A fresh local demo database avoids mixing rehearsal data with genuine reviewers.

## Before the meeting (private rehearsal, not live on the call)

1. Check API connectivity in the UI.
2. Click **Load sample dataset**. The repository contains **50 synthetic material streams**.
3. Click **Run recommendations**. Confirm **50** recommendations are generated.
4. Open **Recommendations**, choose **S001**, then **Open review pack**. Confirm the **ruleset release v1.0.0**, rule provenance and human-review competence panel are visible.
5. Return to **Recommendations**, choose **S022**, open its review pack. Confirm the **hazardous risk/human-review gate**. S022 is **spent acetone solvent**, not a routine recycling recommendation.
6. Open **Scenario screening**, select S001 and click **Run scenario**. Show the screening output but do not save a fabricated observed outcome or verification record for the meeting.
7. Open the **blind reviewer** page in a separate tab: **http://127.0.0.1:5173/?mode=blind-review**. Before submission, the system strategy, risk decision and recommended action must be hidden.
8. Open **http://127.0.0.1:5173/?mode=review-analysis** only if genuinely helpful; with no reviews the correct state is **no reviewer submissions**, not agreement.
9. Close unrelated windows; leave the main app ready on Recommendations or the S001 review pack.

## Live walkthrough (10 minutes of a 30-minute conversation)

| Time | Show | Say |
|---|---|---|
| 0:00–1:00 | Short introduction, no code | “I started with material-flow data and circular-economy options. The difficult question became how to govern the recommendation.” |
| 1:00–3:15 | **S001 — Aluminium machining offcuts**: Recommendations → Open review pack | “The deterministic rule produces a *screening route* and keeps evidence checks explicit. It is not proof that a recycler will accept this alloy or that diversion has happened.” Show rule provenance, screening maturity and **v1.0.0**. |
| 3:15–5:30 | **S022 — Spent acetone solvent**: Recommendations → Open review pack | “This is a hazardous stream. Rather than optimising toward a green answer, the system requires competent human review and records who should assess the classification and handling route.” Show gate, reviewer competence and source boundary. |
| 5:30–7:00 | **Scenario screening**, S001 | “These are operator assumptions about possible quantities, not measured recovery, savings or a verified environmental benefit.” Briefly explain that a separate observed-outcome and internal evidence-review workflow exists, but do not create fabricated outcomes live. |
| 7:00–8:00 | Review pack → **Record professional disagreement** (expand only) | “Reviewers can challenge a rule and give reasoning without rewriting the rule's original decision. We retain the original and record the disagreement separately.” Do not submit a pretend professional challenge. |
| 8:00–9:00 | Blind-review portal in separate tab | “The reviewer judges a case before seeing the system answer; disagreements are kept and reviewer consensus is not treated as ground truth.” Do not submit anything on Deepa's behalf. |
| 9:00–10:00 | Return to review pack | Ask: “If you were assessing this as a governance professional, what would stop you trusting it?” Stop presenting and listen. |

## Boundaries to disclose if asked

- The application is a **working local alpha**, not production software or an independently assured sustainability platform.
- The public guidance links document the **basis of screening rules**, not a legal waste-classification opinion or regulator approval.
- **Ruleset v1.0.0** identifies the deterministic logic and preserves future run histories; it does not certify technical correctness.
- Numeric “confidence/evidence” legacy fields persist for compatibility but are internal heuristics, not probabilities or assurance.
- Human challenges are recorded without automatic override. Reviewer identities are currently **self-declared**; there is no formal authentication/approval authority.
- Blind reviewer workflows are implemented, but **external professional review is still pending** unless real external submissions have actually been received.
- ESG, GHG and EIA views are not full assessment engines; they are outside this demonstration.

## Three questions to give Deepa room to answer

1. “Where are the control boundaries still too weak, especially between AI advice, locked rules, evidence and human judgement?”
2. “What evidence would you need to trust a screened circular opportunity, and which claims would you block?”
3. “What should the approval and challenge process look like when a competent professional disagrees with the locked rule?”

## Meeting completion checklist

- [ ] The two contrasting cases opened without errors
- [ ] Version and rule provenance shown correctly
- [ ] Screened vs observed vs verified distinction explained
- [ ] No synthetic review or evidence described as independent validation
- [ ] At least one governance concern or requirement captured in notes
- [ ] Agree a precise next step only if she is interested (e.g., assess blind methodology or selected cases)

## Test evidence and limitation

Continuous integration includes Python backend tests, the frontend production build, and Playwright-driven Chromium tests of the actual browser workflow. CI is **not a substitute for a rehearsal on the presenter's Windows machine**, especially for browser zoom, screen sharing, firewall or third-party AI availability.

**No live operational data or genuine external reviewer records are necessary for this demo.**
