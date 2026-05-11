# Milestone 13B: Workspace Contract and Architecture Hardening

## Objective

Strengthen the 13A domain workspace architecture before adding deeper ESG, GHG, EIA, claims, supplier or data-profiler features.

This milestone keeps Circular Core as the main industrial circular economy decision-support system while making the app safer to expand into supporting professional intelligence workspaces.

## Why it matters professionally

Circular Industry AI now has multiple top-level workspaces. Without a clearer architecture contract, future features could turn the product into a generic sustainability dashboard with many shallow tabs.

13B prevents that by separating:

- product shell and domain navigation
- Circular Core workflow rendering
- domain workspace metadata
- domain-specific data requirements
- valid outputs
- forbidden or unavailable claims
- evidence requirements

## What files change

Expected files changed or added:

```text
frontend/src/App.jsx
frontend/src/components/CircularCoreWorkspace.jsx
frontend/src/components/DomainWorkspace.jsx
frontend/src/config/domainWorkspaces.js
docs/milestone_13b_workspace_contract_architecture_hardening.md
```

## What does not change

This milestone does not change:

- backend rules engine
- database models
- API routes
- LLM authority
- circular recommendation logic
- risk scoring
- evidence scoring
- review status logic
- claim boundary logic
- verified impact handling

The rules engine remains the locked decision source.

## UX behaviour

The top-level workspace navigation remains clean:

- Circular Core
- ESG
- GHG & Net Zero
- EIA
- Greenwashing / Claims
- Supplier & Procurement
- Data Profiler

Circular Core continues to show the existing operational workflow.

Supporting domain workspaces now show a clearer contract:

- required data
- optional signals
- valid outputs
- unavailable or blocked outputs
- evidence requirements
- parser status

This makes clear that supporting workspaces are not yet full domain engines.

## Governance boundary

AI/LLM may explain, summarise, classify, draft, compare and support investigation.

AI/LLM must not override:

- risk level
- review status
- rule applied
- claim boundary
- evidence controls
- legal/compliance status
- verified impact
- verified savings
- verified carbon reduction
- verified supplier compliance
- verified ESG performance
- statutory EIA significance

## Testing steps

Run from the project root after applying the installer:

```powershell
git diff --check
cd frontend
npm run build
cd ..
git status --short
git diff --stat
```

Manual browser smoke test:

```text
1. App loads without runtime error.
2. Circular Core is still the default workspace.
3. Domain bar displays clean workspace names.
4. Each supporting workspace opens correctly.
5. Return to Circular Core works.
6. Circular Core workflow still loads controls, summary cards, dashboard and workflow nav.
7. Upload/select file in a supporting workspace shows the parser-not-activated message.
8. No wide table or page-breaking layout appears.
```

## Commit message

```text
Add workspace contract architecture hardening
```

## PR title

```text
Milestone 13B: Add workspace contract architecture hardening
```

## PR body

```markdown
## Objective

Adds Milestone 13B: Workspace Contract and Architecture Hardening.

This milestone strengthens the 13A domain workspace architecture before adding deeper domain engines. It keeps Circular Core as the main industrial circular economy decision-support workflow while giving each supporting workspace a controlled data and governance contract.

## Changes

- Moves domain workspace metadata and domain contracts into `frontend/src/config/domainWorkspaces.js`.
- Adds `CircularCoreWorkspace` to separate the core workflow rendering from `App.jsx`.
- Refactors `App.jsx` into a cleaner product shell and workspace router.
- Updates `DomainWorkspace` to render required data, optional signals, valid outputs, blocked outputs and evidence requirements.
- Adds milestone documentation.

## Governance boundary

The rules engine remains the locked decision source.

This milestone does not change backend rules, scoring, API routes, LLM authority, risk logic, review status, claim boundaries, evidence controls or verified impact handling.

Supporting workspaces remain architecture/contracts at this stage. They do not yet perform full ESG, GHG, EIA, claims, supplier or generic profiling analysis.

## Testing

- `git diff --check`
- `npm run build`
- Browser smoke test across domain navigation and Circular Core workflow

## Pre-merge file check

Expected files only:

```text
frontend/src/App.jsx
frontend/src/components/CircularCoreWorkspace.jsx
frontend/src/components/DomainWorkspace.jsx
frontend/src/config/domainWorkspaces.js
docs/milestone_13b_workspace_contract_architecture_hardening.md
```

Do not include installer files, zip files, `frontend/dist/`, `.env`, `.venv`, databases, `node_modules` or temporary files.
```

## Pre-merge file check

Before merge, confirm the PR contains only the expected milestone files and no generated or temporary files.
