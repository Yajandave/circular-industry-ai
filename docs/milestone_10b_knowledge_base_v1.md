# Milestone 10B: Knowledge Base v1

## Purpose

Milestone 10B turns the 10A knowledge architecture into a structured, inspectable internal knowledge base.

The goal is not to copy external repositories into the product. The goal is to curate useful concepts from trusted sources into Circular Industry AI's own controlled JSON knowledge files.

## Added structure

```text
backend/app/knowledge_base/
  loader.py
  data/
    sources/
    materials/
    circular_routes/
    evidence_rules/
    future_horizon/
```

## Seed knowledge included

### Materials

```text
metals
plastics
cardboard_packaging
wood_pallets
chemicals_solvents
batteries
```

### Routes

```text
closed_loop_recycling
supplier_takeback
process_redesign
specialist_recovery
compliant_disposal
```

### Evidence rules

```text
claim_readiness
hazardous_review
supplier_evidence
```

### Future horizon

```text
plastics_advanced_recycling
digital_product_passports
battery_recycling
```

## External knowledge use

External sources are used as references for structure and concepts, not as direct operational proof.

Seed references include:

- Circular Economy Ontology Network
- openLCA schema
- Open Repair Alliance open repair data
- ISO 59040 Product Circularity Data Sheet
- Ellen MacArthur Foundation circular economy principles
- GOV.UK waste and hazardous waste guidance
- European Commission circular economy strategy pages

## Product principle

```text
Raw operational data is input.
Knowledge files provide domain understanding.
The agent generates statements, suggestions and reports.
```

## Governance boundary

The knowledge base supports screening and reasoning. It does not verify legal compliance, supplier capability, carbon savings, financial savings, circularity claims or completed operational impact.
