# Milestone 14A: Data Profiler Engine Foundation

## Objective

Add a backend-first data profiler that can inspect uploaded CSV files, map clean-but-differently-named columns into semantic roles, identify missing fields, and recommend the correct workspace route without forcing the data into the strict Circular Core template.

## Why it matters professionally

Real organisations may provide clean and structured datasets with different column names. For example, a dataset may use `Vendor Name` instead of `supplier`, or `Monthly Weight` instead of `monthly_quantity_kg`.

Circular Industry AI should not require users to copy a rigid template before the system can understand the file. It should profile the uploaded CSV, explain what it can map, show uncertainty, and refuse to invent missing data.

## Files changed

```text
backend/app/data_profiler.py
backend/app/routers/data_profiler.py
backend/app/main.py
backend/app/schemas.py
backend/tests/test_data_profiler.py
frontend/src/api/client.js
frontend/src/components/DomainWorkspace.jsx
frontend/src/components/DataProfilerPanel.jsx
frontend/src/styles.css
docs/milestone_14a_data_profiler_engine_foundation.md
```

## What does not change

This milestone does not change the strict Circular Core CSV import, loaded stream database, rules engine, scoring logic, recommendation generation, evidence register, supplier-loop logic, AI/LLM authority or backend field names.

## Governance boundary

The profiler may map columns and recommend workspace routes. It must not invent missing fields, verify savings, verify diversion, verify environmental impact, confirm supplier compliance, approve sustainability claims, determine legal compliance or determine statutory EIA significance.

## Testing

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
cd ..
cd frontend
npm run build
cd ..
git diff --check
git status --short
git diff --stat
```

## Commit message

```text
Add data profiler engine foundation
```

## PR title

```text
Milestone 14A: Add data profiler engine foundation
```
