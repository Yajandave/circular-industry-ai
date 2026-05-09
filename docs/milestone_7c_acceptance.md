# Milestone 7C Acceptance Criteria

## Milestone title
Rules-locked LLM reasoning layer and UI/table formatting QA

## Objective
Add an optional LLM reasoning layer that improves explanation quality without allowing AI to override the locked rules engine, risk controls, human-review gates or claim boundaries. Improve frontend readability so long tables, review content and evidence outputs wrap cleanly without words colliding.

## Backend acceptance criteria

- `GET /api/ai-reasoning/status` returns whether the optional LLM layer is enabled, whether an API key is configured, the selected model and the active generation mode.
- `POST /api/ai-reasoning/{stream_id}` returns a structured reasoning narrative for a stream.
- If `AI_REASONING_ENABLED=false` or no `OPENAI_API_KEY` is configured, the endpoint returns deterministic fallback reasoning.
- If the OpenAI API call fails, the endpoint falls back to deterministic reasoning and returns a validation warning.
- The LLM is not allowed to change:
  - `rule_applied`
  - `risk_level`
  - `human_review_required`
  - `recommended_circular_action`
  - `claim_boundary`
- The response includes:
  - executive summary
  - circular economy reasoning
  - evidence-gap explanation
  - supplier/contractor questions
  - pilot guidance
  - claim safety note
  - human review note
  - implementation risks
  - validation warnings

## Frontend acceptance criteria

- Workflow includes an **AI reasoning** tab.
- User can select a stream and generate reasoning.
- If the LLM is not configured, fallback reasoning is shown instead of an error.
- The AI reasoning panel clearly shows the active mode and locked controls.
- Long reasoning text is displayed in cards, not squeezed into table columns.
- Long table labels and values wrap cleanly.
- Tables remain horizontally scrollable where necessary.
- Status badges and priority labels do not collide with adjacent text.

## Safety standard

Rules decide. Resolution Engine designs. Optional LLM explains and customises. Evidence register controls claims. Human approves.
