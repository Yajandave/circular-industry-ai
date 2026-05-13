# Milestone 14B - Stabilisation Backlog

## Do now

- Keep Circular Core as the primary product surface.
- Treat supporting domains as strengthening layers, not independent product claims.
- Keep all dashboard/report values framed as screening outputs unless verified evidence exists.
- Review README and docs for stale milestone status after 14B-15B.
- Move next work into foundation and reliability milestones before adding new engines.

## Do next

- Add Data Profiler edge-case test plan and reliability rules.
- Define user-confirmed mapping screen before implementing flexible imports.
- Define saved mapping plans and mapping audit trail before building persistence.
- Pin dependencies and strengthen CI expectations.
- Define market-grade V1 honestly, including exclusions.

## Do not do yet

- Do not build full ESG/GHG/EIA/Claims engines.
- Do not imply external assurance or verified impact.
- Do not present AI outputs as decision authority.
- Do not add more dashboards before import and validation are stronger.
- Do not treat a successful build as sufficient frontend test coverage.

## Risk register

| Risk | Severity | Why it matters | Control path |
|---|---:|---|---|
| Feature sprawl | High | Product becomes broad but shallow | Foundation sequence before features |
| Claim-safety drift | High | UI/report wording could imply verified benefits | Wording audit and locked claim boundaries |
| Profiler overconfidence | High | Wrong mapping could corrupt recommendations | User-confirmed mapping and confidence warnings |
| Weak import auditability | High | Operators cannot defend how data entered the system | Mapping audit trail and saved plans |
| Frontend regression risk | Medium | Build pass does not prove workflow correctness | Add targeted frontend tests |
| Dependency instability | Medium | latest versions can break repeatability | Pin and review dependencies |
| Documentation drift | Medium | Users/reviewers misunderstand current capability | README/status cleanup |
| Premature domain engines | Medium | ESG/GHG/EIA claims may outrun evidence | Keep as supporting domains until engines mature |
