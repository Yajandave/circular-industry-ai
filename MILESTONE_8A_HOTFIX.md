# Milestone 8A Hotfix: Clean optional LLM text artefacts

## Why this patch exists

Your site-wide AI copilot endpoint is working, but the Gemini output showed this formatting issue:

```text
Â£63,120
```

For a portfolio demo, that looks unprofessional.

This hotfix updates:

```text
backend/app/ai_copilot/service.py
```

It adds a small output cleaner that converts common encoding artefacts such as:

```text
Â£ -> GBP
â€™ -> '
â€“ -> -
â€” -> -
```

The rules-engine output is still locked. This only cleans display text from the optional LLM/fallback summary.

## How to apply

Extract this zip into the root of your repo:

```text
E:\Games\Cricket\circular-industry-ai
```

Allow overwrite.

Then restart backend and test:

```powershell
cd backend
uvicorn app.main:app --reload
```

In another terminal:

```powershell
Invoke-RestMethod -Method Get http://127.0.0.1:8000/api/ai-copilot/site-summary | ConvertTo-Json -Depth 5
```

## Commit

```powershell
git add backend/app/ai_copilot/service.py
git commit -m "Clean AI copilot text output artefacts"
```
