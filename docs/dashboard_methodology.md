# Dashboard Methodology

Circular Industry AI uses the dashboard as a prioritisation layer. It does not replace the locked rules engine and does not verify environmental or financial impact.

## Purpose

The dashboard helps a user answer five practical questions:

1. Which circular opportunities look easiest to validate first?
2. Which streams require controlled human review?
3. Which recommendations carry the strongest cost-exposure or diversion potential?
4. Which material categories dominate the portfolio?
5. Where is the evidence too weak to support claims or implementation decisions?

## Priority bands

The frontend calculates a display-only priority band to help users sort and inspect recommendations.

| Priority band | Meaning |
|---|---|
| Quick win | Low-risk, high-confidence, good-evidence item suitable for validation. |
| Opportunity development | Useful opportunity that needs further supplier, process or evidence work. |
| Evidence improvement | The idea may be useful, but the evidence base is not strong enough yet. |
| Controlled review | Risk, hazard, blocked status or review trigger requires formal human review. |

The priority band does not override the backend recommendation, risk level, confidence score, evidence score or human review flag.

## Priority score

The interface calculates a screening score from:

- confidence score
- evidence quality score
- estimated annual diversion potential
- estimated annual disposal cost exposure
- risk penalty
- human review penalty

This is used only for sorting and dashboard navigation.

## Claim boundary

The dashboard uses phrases such as `cost exposure`, `diversion potential` and `screening output` because the values are not verified operational outcomes. They are estimates based on uploaded stream data and rules-engine calculations.

Do not claim:

- verified annual savings
- verified carbon savings
- verified waste diversion
- legal by-product status
- supplier compliance
- safe recovery route

until implementation evidence is collected and reviewed.
