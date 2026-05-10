# Milestone 9B: AI Runtime Reliability and Agentic Mode Hardening

## Purpose

Milestone 9B makes the AI layer more product-grade.

The goal is not to make AI take over decisions. The goal is to make AI runtime status visible, bounded and fallback-safe.

## New endpoint

```text
GET /api/ai-runtime/status
```

This reports:

- whether AI reasoning is enabled
- configured provider
- configured model
- whether an API key is configured
- request timeout
- runtime mode
- fallback availability
- guardrail summary
- recommended operator action

## Runtime modes

```text
ai_on
fallback_key_missing
fallback_ai_disabled
```

## Timeout hardening

The existing hardcoded 45-second LLM timeout is replaced with:

```text
LLM_TIMEOUT_SECONDS
```

Default:

```text
20 seconds
```

Bounded range:

```text
3 to 60 seconds
```

This prevents AI calls from hanging the product workflow indefinitely.

## Frontend visibility

The frontend now shows an AI runtime status panel with:

- AI-on or fallback mode
- provider
- model
- timeout
- fallback status
- guardrail summary

## Stability fix

Milestone 9B also fixes the missing `circularActionReport` state declaration in the frontend app.

## Product boundary

Circular Industry AI remains AI-powered but not AI-fragile.

The correct business-grade behaviour is:

```text
AI-on when provider is configured and available.
Fallback-safe when provider is unavailable, disabled, slow or missing.
Rules and evidence remain locked either way.
```
