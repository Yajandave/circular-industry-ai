# Milestone 8A: Site-Wide AI Copilot Backend Layer

## What this zip adds

This repo overlay adds:

- `backend/app/ai_copilot/`
- `backend/app/routers/ai_copilot.py`
- updated `backend/app/main.py`
- updated `backend/app/schemas.py`

New endpoint:

```text
GET /api/ai-copilot/site-summary
```

The endpoint generates a site-wide AI copilot summary from locked rules-engine outputs.

## Safety boundary

The AI copilot is advisory only.

It must not override:

- risk level
- human review status
- rule applied
- recommended circular action
- claim boundary
- legal/compliance status
- verified impact

## How to install

Extract this zip into the root of your repo:

```text
circular-industry-ai/
```

Allow overwrite when prompted.

## Recommended Git commands

```powershell
git checkout main
git pull
git checkout -b milestone-8a-site-wide-ai-copilot
```

After extracting:

```powershell
git status
git add backend/app/ai_copilot backend/app/routers/ai_copilot.py backend/app/main.py backend/app/schemas.py MILESTONE_8A_INSTALL.md
git commit -m "Add site-wide AI copilot backend summary endpoint"
```

## Test commands

Start backend:

```powershell
cd backend
uvicorn app.main:app --reload
```

In another terminal:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/streams/load-sample
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/recommendations/run
Invoke-RestMethod -Method Get http://127.0.0.1:8000/api/ai-copilot/site-summary
```

## Fallback mode

The endpoint works without Gemini or OpenAI. If no key is configured, it returns a deterministic fallback summary.

## Gemini mode

Use your backend `.env`, never frontend `.env`:

```env
AI_REASONING_ENABLED=true
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_new_key_here
```

Do not paste API keys into chat.
