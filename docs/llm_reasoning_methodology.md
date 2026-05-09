# LLM Reasoning Methodology

Milestone 7C adds an optional rules-locked LLM reasoning layer. The LLM is not a decision-maker. It is a controlled explanation and drafting layer that uses locked context from the existing system.

## Context package

Each LLM request is built from:

1. Uploaded stream data
2. Locked rules-engine recommendation
3. Evidence register record
4. Circular resolution plan
5. Non-negotiable controls

The LLM is instructed not to change the locked recommendation, risk level, human-review status, rule applied or claim boundary.

## Model approach

This project uses a hybrid architecture:

- deterministic rules for circular route selection
- scoring for risk, evidence and confidence
- circular resolution engine for intervention design
- optional structured LLM output for readable reasoning
- backend validation for safety and consistency

This avoids relying on a free-form chatbot response.

## Structured output fields

The optional LLM returns:

- executive summary
- circular economy reasoning
- evidence-gap explanation
- supplier questions
- pilot guidance
- claim safety note
- human review note
- implementation risks

If the LLM is disabled, missing an API key or fails, a deterministic fallback response is generated from the same locked context.

## Guardrails

The AI layer cannot:

- lower risk level
- remove human review
- change the rule applied
- approve hazardous or unknown streams
- confirm supplier compliance
- verify legal waste status
- claim verified savings
- claim verified carbon reduction

## Environment variables

```env
AI_REASONING_ENABLED=false
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5-mini
OPENAI_REASONING_EFFORT=low
```

Keep `AI_REASONING_ENABLED=false` unless an API key is configured and the user wants live LLM output.

## Gemini free-tier configuration

Milestone 7C can use Gemini as the live LLM provider. The project uses the same guardrail model as OpenAI: the rules engine stays locked, the resolution engine supplies the intervention context, and the LLM only writes structured reasoning.

Recommended local `backend/.env`:

```env
AI_REASONING_ENABLED=true
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_MODEL=gemini-2.5-flash
GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta
```

The variable is still called `OPENAI_MODEL` because the first version of the LLM layer used OpenAI naming. For Gemini, set it to a Gemini model such as `gemini-2.5-flash`.

Never place real API keys in frontend code, GitHub, screenshots or documentation.
