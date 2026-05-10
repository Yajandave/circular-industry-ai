# Milestone 10A: Circular Industry AI Knowledge Architecture v1

## Purpose

Circular Industry AI should not depend on pre-written circular economy statements inside uploaded datasets.

The product goal is:

```text
Raw operational/business data in
Agent-generated circular economy interpretation out
```

This document defines the knowledge architecture required to make the system behave like an agentic circular economy analyst while keeping decisions auditable, claim-safe and commercially realistic.

---

## 1. Product intelligence thesis

Circular Industry AI should become an agentic circular economy intelligence system that can take raw industrial, operational, procurement and waste-stream data and generate:

- material-specific interpretation
- risk and compliance feedback
- circular economy opportunities
- evidence gaps
- supplier/procurement questions
- implementation actions
- current-action recommendations
- future-watch opportunities
- claim boundaries
- reports and decision records

The agent should not rely on narrative notes being present in the dataset.

### Core principle

```text
Numbers and categories are inputs.
Statements, explanations and recommendations are outputs.
```

---

## 2. Knowledge architecture overview

The agent requires a structured knowledge brain made of these layers:

```text
1. Circular economy principles
2. Current standards and reporting frameworks
3. Waste and compliance guardrails
4. Material-family playbooks
5. Industrial process knowledge
6. Circular route playbooks
7. Evidence and claim-readiness rules
8. Procurement and supplier-loop knowledge
9. Data-quality and import-readiness logic
10. Sector-specific opportunity maps
11. Emerging technology and policy horizon scanner
12. Outcome-learning layer
```

The knowledge system must combine:

```text
curated knowledge library
+ source registry
+ material/process mappings
+ rules engine
+ retrieval layer
+ AI reasoning layer
+ audit trail
+ feedback/outcome layer
```

---

## 3. Source hierarchy

The agent must not treat all knowledge sources equally.

### Tier 1: Governance and compliance sources

Use for hard guardrails.

Examples:

- Government waste classification guidance
- Hazardous waste guidance
- Environmental regulator guidance
- Legal/regulatory texts
- Official standards bodies

Allowed use:

```text
decision boundary
human-review trigger
claim restriction
legal/compliance caution
```

### Tier 2: International standards and reporting frameworks

Use for reporting logic, circular economy vocabulary and measurement boundaries.

Examples:

- ISO 59004
- ISO 59010
- ISO 59020
- ISO 59040
- ESRS E5
- waste hierarchy frameworks

Allowed use:

```text
framework alignment
measurement design
evidence requirements
reporting language
```

### Tier 3: Recognised circular economy institutions

Use for core principles and strategy logic.

Examples:

- Ellen MacArthur Foundation
- UNEP / ISWA reports
- OECD / EU circular economy policy resources

Allowed use:

```text
circular economy worldview
strategic framing
route hierarchy
future trend interpretation
```

### Tier 4: Industry and technical sources

Use for material/process-specific feasibility.

Examples:

- recycler guidance
- supplier technical documents
- trade association guidance
- manufacturer documents
- procurement frameworks
- sector case studies

Allowed use:

```text
supplier questions
technical feasibility prompts
route screening
commercial checks
```

### Tier 5: Emerging research and innovation sources

Use only for future-watch or pilot-stage suggestions unless commercially proven.

Examples:

- peer-reviewed research
- R&D announcements
- pilot project reports
- technology demonstrators
- innovation grants
- academic/industry partnerships

Allowed use:

```text
future watch
pilot exploration
innovation monitoring
not verified recommendation
```

---

## 4. Maturity labels

Every suggestion must be labelled by maturity.

```text
available_now
pilot_ready
emerging
research_stage
not_recommended
```

### available_now

A route is commercially available and commonly actionable with normal due diligence.

Example:

```text
segregated aluminium scrap recycling
supplier packaging take-back
cardboard baling and recycling
wood pallet repair/reuse
```

### pilot_ready

A route may be viable but needs a controlled trial.

Example:

```text
supplier closed-loop polymer return
food residue industrial symbiosis
returnable packaging loop
process-water reuse trial
```

### emerging

A route is developing commercially but may not be widely available or suitable.

Example:

```text
selected chemical recycling routes
digital product passport-enabled traceability
advanced sorting systems
specialist textile-to-textile recycling
```

### research_stage

A route is scientifically interesting but not suitable for normal operational recommendation.

Example:

```text
early-stage enzymatic or photochemical plastic conversion research
novel bio-based conversion routes without local commercial pathway
```

### not_recommended

A route should not be suggested except as a caution.

Example:

```text
reuse of hazardous/unknown waste without classification
unverified carbon-neutral claims
uncontrolled mixing of contaminated streams
```

---

## 5. Agent decision authority

The agent must separate locked decisions from advisory intelligence.

### Locked by rules/system

The AI must not override:

- risk level
- human-review status
- rule applied
- hazardous/unknown escalation
- claim boundary
- evidence status
- review gate
- verified impact status
- legal/compliance status

### AI may generate

The AI can generate:

- explanation
- evidence gap reasoning
- supplier questions
- procurement prompts
- implementation steps
- future-watch suggestions
- report wording
- action plan wording
- issue summaries
- route comparison language

### Human must decide

Humans must confirm:

- legal waste classification
- hazardous status
- supplier acceptance
- contract terms
- operational feasibility
- verified diversion
- verified cost saving
- verified carbon saving
- public claims

---

## 6. Input data expectations

The product should work from minimal operational fields.

### Required core fields

```text
stream_id
stream_name
material
source_process
monthly_quantity_kg
current_route
disposal_cost_per_month
contamination_risk
hazardous_flag
department
supplier
supplier_takeback_available
recycled_content_available
```

### Optional fields

```text
notes
waste_code
site_area
storage_method
collection_frequency
contractor
recycler
SDS_available
photos_available
weighbridge_records_available
supplier_contract_status
```

### Important rule

`notes` must be useful but non-essential.

The agent should still generate meaningful insight when `notes` is blank.

---

## 7. Generated output classes

For each stream, the agent should generate these output classes:

### 1. Current action

What can safely be explored now?

Example:

```text
Segregate aluminium offcuts by alloy/grade and confirm recycler acceptance criteria.
```

### 2. Evidence gap

What evidence is missing before action/claim?

Example:

```text
Need alloy grade, contamination check, collection records and recycler acceptance criteria.
```

### 3. Supplier/procurement action

What should procurement ask?

Example:

```text
Ask supplier/recycler for take-back acceptance criteria, contamination limits, minimum volume and documentation.
```

### 4. Human-review trigger

What needs expert review?

Example:

```text
Hazardous or unknown status requires EHS/waste specialist review before route selection.
```

### 5. Future-watch route

What emerging option should be monitored?

Example:

```text
Monitor chemical/enzymatic recycling only if polymer composition and contamination make mechanical recycling unsuitable.
```

### 6. Claim boundary

What must not be claimed?

Example:

```text
Do not claim verified diversion, cost saving or carbon saving until operational evidence confirms the route and outcome.
```

---

## 8. Evidence-to-claim ladder

The agent must classify every output by evidence maturity.

```text
idea
screening_estimate
supplier_indicated
pilot_validated
measured
verified
audited
```

### idea

Generated from material/process knowledge. No direct evidence yet.

### screening_estimate

Calculated from uploaded quantity/cost data but not operationally verified.

### supplier_indicated

Supplier has stated a route may exist, but no operational proof yet.

### pilot_validated

Trial has been run with documented results.

### measured

Actual quantities/costs/outcomes have been measured.

### verified

Evidence has been checked against records.

### audited

Evidence has been independently or formally reviewed.

---

## 9. Material-family knowledge schema

Each material playbook should use this structure.

```json
{
  "material_family": "aluminium",
  "common_streams": ["machining offcuts", "sheet offcuts", "extrusion scrap"],
  "typical_sources": ["CNC machining", "metal fabrication", "assembly"],
  "available_now_routes": ["segregated recycling", "closed-loop recycler review", "supplier take-back"],
  "pilot_ready_routes": ["closed-loop return to supplier", "grade-specific recovery trial"],
  "future_watch_routes": ["digital product passport-enabled traceability for product components"],
  "blocked_by": ["mixed alloy grades", "oil/coolant contamination", "paint/coating contamination"],
  "evidence_required": ["alloy grade", "segregation method", "contamination check", "weighbridge records", "recycler acceptance criteria"],
  "supplier_questions": ["Can you accept segregated aluminium offcuts?", "What alloy and contamination limits apply?"],
  "human_review_triggers": ["unknown contamination", "hazardous coating", "unclear contractor route"],
  "unsafe_claims": ["verified carbon saving without emissions method", "closed-loop recycling without recycler confirmation"],
  "default_claim_boundary": "screening only until recycler acceptance and movement records are available"
}
```

---

## 10. Material families required for v1

Minimum v1 material intelligence library:

```text
metals
plastics
paper_cardboard
wood_pallets
glass
rubber
textiles
organics_food_residue
process_water
chemicals_solvents
batteries
electronics_WEEE
construction_demolition
composites
packaging
industrial_sludge_mineral_residue
oils_lubricants
```

---

## 11. Industrial process knowledge

The agent should understand waste/by-product patterns from:

```text
CNC machining
metal fabrication
injection moulding
extrusion
painting/coating
assembly
packaging
warehouse operations
food processing
chemical cleaning
maintenance
quality rejects
water treatment
construction fit-out
laboratory operations
events and temporary installations
```

Example logic:

```text
If material = metal swarf
and process = machining
then ask about coolant contamination, alloy grade and collection method.
```

---

## 12. Circular route playbook schema

Each route should have:

```json
{
  "route": "supplier_takeback",
  "route_strength": "medium_to_high",
  "best_for": ["packaging", "clean production scrap", "returnable transit materials"],
  "not_suitable_for": ["hazardous unknown waste", "mixed contaminated streams"],
  "required_data": ["supplier name", "volume", "material type", "contamination level"],
  "required_evidence": ["acceptance criteria", "contract clause", "collection record"],
  "implementation_steps": ["contact supplier", "confirm acceptance", "run trial", "track quantities"],
  "claim_boundary": "Supplier take-back can be described as under review until actual collection and destination records are available."
}
```

---

## 13. Future-facing horizon scanner

The agent needs a future opportunity layer.

Track areas such as:

```text
chemical recycling
enzymatic plastic recycling
AI-enabled material sorting
robotic disassembly
digital product passports
battery recycling and critical raw material recovery
textile-to-textile recycling
construction material passports
industrial symbiosis marketplaces
biochar and nutrient recovery
anaerobic digestion
water reuse and recirculation technologies
right-to-repair policy
extended producer responsibility
secondary raw material markets
```

Each future item should be stored with:

```json
{
  "topic": "chemical recycling for mixed plastics",
  "material_family": "plastics",
  "maturity": "emerging",
  "confidence": "medium",
  "source_type": "policy / research / industry",
  "last_checked": "2026-05-10",
  "allowed_use": "future_watch_only",
  "claim_boundary": "Do not present as verified or commercially available without supplier/recycler evidence."
}
```

---

## 14. Current action vs future-watch output format

Every agent suggestion should be split like this:

```text
Current action:
What can safely be explored now.

Near-future action:
What could be prepared or piloted soon.

Future watch:
What should be monitored but not operationally recommended yet.

Evidence needed:
What would upgrade this suggestion.

Do not claim:
What the user must not present as verified.
```

Example:

```text
Current action:
Improve segregation of PET-rich plastic trim and confirm polymer grade.

Near-future action:
Ask specialist recyclers whether they can accept the stream if contamination is controlled.

Future watch:
Monitor chemical or enzymatic recycling only if mechanical recycling remains unsuitable.

Evidence needed:
Polymer composition, contamination assessment, recycler acceptance and collection records.

Do not claim:
Do not claim closed-loop recycling or carbon savings until actual route evidence exists.
```

---

## 15. Retrieval and reasoning flow

The AI reasoning flow should be:

```text
1. Receive raw stream data
2. Run data-quality checks
3. Extract features:
   - material
   - process
   - quantity
   - cost
   - contamination
   - hazardous status
   - supplier status
4. Retrieve matching material/process/route knowledge
5. Apply locked rules
6. Generate advisory explanation
7. Generate current action, near-future action and future-watch route
8. Attach evidence requirements and claim boundary
9. Record audit event
```

---

## 16. What the AI must not do

The AI must not:

- invent supplier capability
- invent legal compliance
- invent verified cost savings
- invent verified carbon savings
- invent waste classification
- claim hazardous materials are safe
- recommend reuse/recycling for unknown hazardous streams without review
- present research-stage technologies as operationally available
- treat future-watch routes as confirmed actions
- override locked rules

---

## 17. Knowledge update process

The knowledge brain must be maintainable.

Each knowledge item should include:

```text
source_name
source_url
source_type
jurisdiction
topic
material_family
maturity
confidence
last_checked
review_frequency
allowed_use
claim_boundary
```

Recommended refresh cadence:

```text
Regulation/compliance: monthly or when changed
Standards/reporting: quarterly
Material playbooks: quarterly
Emerging research: monthly
Supplier/market routes: quarterly
Internal outcome learning: continuous
```

---

## 18. Outcome-learning layer

Future versions should learn from actual outcomes.

Required future records:

```text
SupplierResponse
PilotOutcome
VerifiedImpact
UserDecision
EvidenceUpload
RecommendationFeedback
```

The system should learn patterns such as:

```text
which suppliers accept take-back
which material streams repeatedly fail due to contamination
which evidence gaps most often block claims
which circular routes produce measured savings
which future-watch routes become commercially viable
```

This is the path from AI-assisted analysis to outcome-informed intelligence.

---

## 19. Implementation roadmap after 10A

### 10B: Knowledge Base v1

Create structured YAML/JSON knowledge files for materials, processes, routes, evidence and future-watch topics.

### 10C: Material Intelligence Engine

Generate stream-level insights from raw fields without relying on notes.

### 10D: Future Opportunity Horizon Scanner

Add maturity-labelled future opportunity suggestions.

### 10E: Evidence-to-Claim Upgrade Engine

Upgrade/downgrade recommendations based on evidence maturity.

### 10F: Outcome Learning Foundation

Track supplier responses, user decisions and pilot results.

---

## 20. Definition of done for 10A

10A is complete when the repository contains:

```text
docs/knowledge_architecture_v1.md
docs/knowledge_source_registry_v1.md
docs/agent_intelligence_boundaries_v1.md
```

And the product direction is clear:

```text
The dataset supplies raw operational facts.
The knowledge brain supplies domain understanding.
The rules engine supplies locked decisions.
The AI supplies generated interpretation and next actions.
The human supplies verification and final approval.
```
