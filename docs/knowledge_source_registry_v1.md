# Circular Industry AI Knowledge Source Registry v1

This registry defines the source categories and initial seed sources for the Circular Industry AI knowledge brain.

The purpose is to keep the agent current, evidence-aware and future-facing without allowing it to make unsafe claims.

---

## Source use categories

```text
governance_guardrail
standard_or_reporting_framework
circular_economy_principle
material_route_knowledge
future_horizon
market_signal
research_watch
```

---

## Seed source registry

| Source | URL | Category | Use in agent | Refresh cadence |
|---|---|---|---|---|
| Ellen MacArthur Foundation circular economy principles | https://www.ellenmacarthurfoundation.org/circular-economy-principles | circular_economy_principle | Core CE framing: eliminate waste/pollution, circulate products/materials, regenerate nature | Quarterly |
| ISO 59004:2024 | https://www.iso.org/standard/80648.html | standard_or_reporting_framework | Circular economy vocabulary, principles and implementation guidance | Quarterly |
| ISO 59010:2024 | https://www.iso.org/standard/80649.html | standard_or_reporting_framework | Business models and value networks transition logic | Quarterly |
| ISO 59020:2024 | https://www.iso.org/standard/80650.html | standard_or_reporting_framework | Circularity measurement and assessment logic | Quarterly |
| ESRS E5 Resource use and circular economy | https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32023R2772 | standard_or_reporting_framework | Resource inflow/outflow/waste reporting structure | Quarterly |
| GOV.UK classify waste | https://www.gov.uk/guidance/classify-different-types-of-waste-your-legal-responsibilities | governance_guardrail | Waste classification and legal responsibility guardrails | Monthly |
| GOV.UK hazardous waste | https://www.gov.uk/dispose-hazardous-waste | governance_guardrail | Hazardous waste duty-of-care and escalation logic | Monthly |
| European Commission Circular Economy | https://environment.ec.europa.eu/strategy/circular-economy_en | future_horizon | EU circular economy policy direction | Monthly |
| Ecodesign for Sustainable Products Regulation | https://commission.europa.eu/energy-climate-change-environment/standards-tools-and-labels/products-labelling-rules-and-requirements/ecodesign-sustainable-products-regulation_en | future_horizon | Product design, circularity, DPP and sustainable product requirements | Monthly |
| UNEP Global Waste Management Outlook 2024 | https://www.unep.org/resources/global-waste-management-outlook-2024 | future_horizon | Global waste trend context and circular economy urgency | Quarterly |

---

## Source metadata schema

Future structured knowledge items should use:

```json
{
  "source_name": "GOV.UK hazardous waste",
  "source_url": "https://www.gov.uk/dispose-hazardous-waste",
  "source_type": "government_guidance",
  "jurisdiction": "England / UK",
  "topic": "hazardous waste duty of care",
  "material_family": "cross_material",
  "maturity": "current_governance",
  "confidence": "high",
  "last_checked": "2026-05-10",
  "review_frequency": "monthly",
  "allowed_use": "governance_guardrail",
  "claim_boundary": "Use to trigger caution/human review; do not treat as legal advice."
}
```

---

## Source quality rules

The agent should prioritise sources in this order:

```text
1. Official regulation/guidance
2. International standards
3. Recognised circular economy institutions
4. Peer-reviewed research
5. Industry reports and technical guidance
6. News/market signals
7. Supplier claims, only as unverified input
```

Supplier claims are never treated as verified truth without evidence.

---

## Future-horizon source rules

Future-facing suggestions must include:

```text
maturity label
confidence rating
evidence needed
claim boundary
```

Future research can support:

```text
monitor this
investigate this
ask supplier/recycler about this
prepare data for this
```

Future research cannot support:

```text
claim this works
claim this is commercially available
claim verified impact
override hazardous/compliance controls
```
