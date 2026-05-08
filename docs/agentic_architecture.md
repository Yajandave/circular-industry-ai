# Agentic Architecture

Milestone 4 upgrades Circular Industry AI from a rules-only API into a controlled multi-agent decision-support workflow.

## Design principle

The system is advanced underneath but should remain easy for a sustainability, procurement or operations user to use.

The rules engine remains the source of truth. The agentic layer does not make the base circular economy decision. It reviews and enriches an already generated recommendation.

```text
industrial stream + rules recommendation
→ evidence auditor
→ risk reviewer
→ procurement reviewer
→ industrial symbiosis reviewer
→ resource efficiency reviewer
→ executive synthesis
→ review pack / management summary / action plan
```

## Specialist agents

| Agent | Purpose |
|---|---|
| Evidence auditor | Separates measured data, estimated data, assumptions and missing evidence |
| Risk reviewer | Explains high-risk triggers, review gates and decision locks |
| Procurement reviewer | Creates supplier questions, take-back checks and circular procurement levers |
| Industrial symbiosis reviewer | Screens whether the stream could be useful to another process or organisation |
| Resource efficiency reviewer | Checks reduction and process-improvement opportunities before end-of-pipe routes |
| Executive synthesis | Converts technical output into management-ready decision language |

## Governance control

The agentic layer cannot:

- lower a risk level
- remove a human-review flag
- replace the rules engine recommendation
- verify legal waste status
- verify supplier compliance
- make carbon-saving claims
- approve hazardous or contaminated stream actions

## Why this is industrial-grade

The project now resembles a decision-support workflow rather than a chatbot:

- deterministic rules provide auditability
- agentic reviewers add specialist lenses
- evidence and assumptions are separated
- high-risk streams are controlled
- management summaries are generated from structured outputs
- action plans are ranked using confidence, evidence, value and risk

## Endpoint layer

```text
GET /api/agent/review-pack/{stream_id}
GET /api/agent/management-summary
GET /api/agent/action-plan
```

These endpoints are designed for the future React frontend. The user should eventually see simple cards, tables and review packs, while the backend handles the more advanced workflow.
