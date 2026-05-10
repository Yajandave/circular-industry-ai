# Milestone 10B Install Notes

## Important order

Create the branch before extracting the zip:

```powershell
cd E:\Games\Cricket\circular-industry-ai
git checkout main
git pull
git checkout -b milestone-10b-knowledge-base-v1
```

Then extract the zip into the repo root.

## Test backend

```powershell
cd E:\Games\Cricket\circular-industry-ai\backend
.\.venv\Scripts\python.exe -m pytest
```

## Commit

```powershell
cd E:\Games\Cricket\circular-industry-ai

git add backend/app/knowledge_base backend/tests/test_knowledge_base.py docs/milestone_10b_knowledge_base_v1.md MILESTONE_10B_INSTALL.md

git commit -m "Add Circular Industry AI knowledge base v1"
git push -u origin milestone-10b-knowledge-base-v1
```

## PR title

```text
Add Circular Industry AI knowledge base v1
```

## PR description

```markdown
## Summary
Adds Milestone 10B: structured Knowledge Base v1 for Circular Industry AI.

## Key additions
- Added source registry with controlled external references
- Added seed material-family knowledge files
- Added circular route knowledge files
- Added evidence-rule knowledge files
- Added future-horizon knowledge files
- Added knowledge-base loader and structural validator
- Added backend tests for knowledge-base validity

## Product principle
External sources are used as curated references. Circular Industry AI stores its own controlled knowledge files and uses them to generate statements from raw data.

## Governance boundary
The knowledge base supports screening and reasoning. It does not verify legal compliance, supplier acceptance, circularity claims, carbon savings or operational impact.
```
