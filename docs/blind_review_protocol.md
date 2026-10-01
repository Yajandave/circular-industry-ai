# Blind decision review protocol

Milestone 20C.4 provides infrastructure for reviewer-versus-system comparison. It does **not** itself create independent validation.

## Purpose

A reviewer evaluates industrial material-stream cases without seeing Circular Industry AI's recommendation, rule, grounded validation constraints or expected answer.

The reviewer records:

- screening-level strategy category
- risk level
- whether human review is required
- confidence from 1 to 5
- written reasoning

Only after submission does the system compare the review with a contemporaneous snapshot of its own output.

## Blind-review sequence

### Preferred reviewer interface

Share only the dedicated reviewer-mode frontend URL:

`<frontend-base-url>/?mode=blind-review`

The reviewer portal:

- loads the blind case pack without exposing system answers
- requires reviewer name, professional role and blind declaration
- requires all 10 current cases before submission
- captures strategy category, risk level, human-review requirement, confidence and reasoning
- unlocks the reviewer-versus-system comparison only after successful submission
- can print or save the complete blind case pack as PDF

### API sequence

1. Retrieve `GET /api/decision-validation/blind-review-pack`.
2. Give the reviewer only that pack.
3. Do not show the reviewer:
   - Circular Industry AI recommendations
   - rule IDs
   - 20C.1 internal benchmark labels
   - 20C.2 grounded constraints or interpretations
   - challenge-summary results
4. The reviewer evaluates cases independently and records one structured label per case.
5. Submit those labels through `POST /api/decision-validation/blind-review-submit`.
6. Review agreement metrics only after submission.
7. Preserve reviewer identity, role, organisation where applicable, reasoning and the blind declaration.

## Interpretation

The software reports strategy-category, risk-level and human-review agreement separately. Exact strategy-category agreement is intentionally treated as a coarse metric because two competent reviewers may use different category wording or prioritisation while reaching similar practical conclusions.

A stored review should only be described as **independent expert validation** when there is evidence that:

- the reviewer had relevant professional competence
- the reviewer was sufficiently independent of development of the system
- the reviewer did not see the system output before making their judgement
- the reviewed case set was appropriate for the intended claim
- disagreements and limitations were retained rather than removed

The software cannot prove those conditions by itself.

## Current case set

The blind pack currently uses the 10 England-focused cases from the externally grounded 20C.2 challenge suite, but removes the guidance interpretation, constraints, source catalogue and system answer.

This is a first external-review protocol, not a statistically representative industry validation study.

## Claim boundary

Do not report a high agreement percentage as proof that the product is legally compliant, regulator-approved, independently assured, universally accurate or production-ready.


## Alpha access-control limitation

Reviewer mode isolates the reviewer UI from the normal operator interface, but it is not an authentication or authorisation boundary.

A technically capable reviewer with direct access to the main application or API could deliberately navigate outside reviewer mode. For a controlled review:

- give the reviewer only the reviewer-mode URL
- do not give them the normal operator URL or validation-summary endpoints before submission
- document the review session and blind declaration
- for stronger commercial validation, add authentication and reviewer-specific access controls before relying on the software alone to enforce blinding
