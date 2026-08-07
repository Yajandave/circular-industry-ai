# Security policy

## Current product boundary

Circular Industry AI is an Alpha-stage screening product. It is not currently approved for confidential company data, hazardous-waste routing, legal compliance decisions, verified sustainability claims or unsupervised production use.

Use synthetic or properly anonymised data until authentication, organisation isolation, deployment controls, backups and an independent security review are complete.

Manual audit-event creation is disabled by default. `ALLOW_MANUAL_AUDIT_EVENTS=true` is reserved for controlled local testing and must not be enabled on a shared deployment before authentication and operator roles exist.

## Reporting a vulnerability

Do not disclose a suspected vulnerability in a public issue. Contact the repository owner privately through their GitHub profile and include:

- the affected component and version;
- reproducible steps;
- the likely impact;
- any suggested mitigation.

Do not include real company data, credentials or personal information in a report.

## Dependency position

Backend runtime and test dependencies are pinned and checked in continuous integration with `pip-audit`.

Frontend runtime dependencies are separated from Vite build tooling. Continuous integration checks all npm packages with `npm audit` and verifies the production build. Vite is not shipped as browser runtime code, but build-tool advisories are still treated as blocking until updated or explicitly reviewed.
