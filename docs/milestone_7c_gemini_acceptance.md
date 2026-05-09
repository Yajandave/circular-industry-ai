# Milestone 7C Gemini compatibility patch

## Objective
Enable the optional rules-locked LLM reasoning layer to use the Gemini Developer API free tier while preserving deterministic fallback behaviour and locked decision controls.

## What changed
- Added provider selection with `LLM_PROVIDER=gemini` or `LLM_PROVIDER=openai`.
- Added standard-library `.env` loading from `backend/.env` or repo `.env`.
- Added Gemini structured JSON output support through the Gemini `generateContent` endpoint.
- Added `backend/.env.example` with safe Gemini defaults.
- Updated AI reasoning status output to show provider, model and base URL.
- Kept deterministic fallback active when the API key is missing, disabled or request fails.

## Recommended free-tier configuration

Create `backend/.env` from `backend/.env.example` and use:

```env
AI_REASONING_ENABLED=true
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_MODEL=gemini-2.5-flash
GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta
```

## Acceptance checks
1. `GET /api/ai-reasoning/status` returns `llm_provider: gemini` when configured.
2. With no key, `POST /api/ai-reasoning/S001` returns deterministic fallback instead of crashing.
3. With a valid Gemini key, `POST /api/ai-reasoning/S001` returns structured reasoning.
4. `risk_level`, `human_review_required`, `rule_applied` and claim boundaries remain locked.
5. Frontend AI reasoning tab displays provider and model.

## Safety rule
The LLM can explain and draft. It cannot approve a route, lower risk, remove human review, verify supplier compliance, verify legal status, or make carbon/circularity claims without evidence.
