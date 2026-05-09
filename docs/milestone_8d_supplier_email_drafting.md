# Milestone 8D: AI Supplier Email and Evidence Request Drafting

## Purpose

Milestone 8D converts locked supplier-loop and evidence-register outputs into cautious supplier evidence request emails.

The feature helps a user ask suppliers or recovery contractors for:

- take-back acceptance criteria
- recycled-content documentation
- route evidence
- contamination limits
- collection and reverse-logistics requirements
- rejection rules
- data needed for internal audit

## Governance boundary

The drafting layer is advisory only.

It cannot override:

- risk level
- human review status
- rule applied
- recommendation route
- evidence status
- claim readiness
- supplier-loop route
- review gate
- claim boundary
- verified impact

It must not invent supplier capability, verified savings, legal compliance, carbon impact or route acceptance.

## Backend endpoint

```text
POST /api/procurement/supplier-loops/{stream_id}/email-draft
```

## Frontend location

The feature appears inside:

```text
Supplier loops
```

Users can generate a supplier evidence request draft from top supplier actions or plan cards.

## Portfolio value

This milestone connects circular economy analytics to practical workplace action:

```text
analysis -> evidence gap -> supplier request -> audit trail
```

That is highly relevant for sustainability, ESG, circular procurement and environmental analyst roles.
