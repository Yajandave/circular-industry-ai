# Milestone 10A Install Notes

## Purpose

Milestone 10A is a specification/documentation milestone.

It defines the Circular Industry AI knowledge brain before building the next code layer.

## Important order

Create the branch before extracting the zip:

```powershell
cd E:\Games\Cricket\circular-industry-ai
git checkout main
git pull
git checkout -b milestone-10a-knowledge-architecture-v1
```

Then extract this zip into the repo root.

## Files added

```text
docs/knowledge_architecture_v1.md
docs/knowledge_source_registry_v1.md
docs/agent_intelligence_boundaries_v1.md
MILESTONE_10A_INSTALL.md
```

## Commit

```powershell
cd E:\Games\Cricket\circular-industry-ai

git add docs/knowledge_architecture_v1.md docs/knowledge_source_registry_v1.md docs/agent_intelligence_boundaries_v1.md MILESTONE_10A_INSTALL.md

git commit -m "Add Circular Industry AI knowledge architecture"
git push -u origin milestone-10a-knowledge-architecture-v1
```

## PR title

```text
Add Circular Industry AI knowledge architecture
```

## PR description

```markdown
## Summary
Adds Milestone 10A: Circular Industry AI Knowledge Architecture v1.

## Key additions
- Defines the agentic knowledge brain
- Separates raw input data from generated interpretation
- Defines source hierarchy and knowledge update rules
- Defines current-action, near-future and future-watch output structure
- Defines material, process, route, evidence and horizon-scanning knowledge layers
- Defines AI decision boundaries and claim-safety rules
- Adds source registry seed for current and future-facing knowledge

## Product principle
Raw data is input. Statements, suggestions, feedback and reports are generated outputs.

## Governance boundary
The AI may explain, suggest and draft, but it must not invent legal compliance, supplier acceptance, verified savings, carbon impact or claim readiness.
```
