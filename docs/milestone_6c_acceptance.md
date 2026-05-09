# Milestone 6C Acceptance Criteria

## Objective

Improve the product workflow and domain-specific review wording after Milestone 6B made the interface portfolio-ready but still too data-heavy on one screen.

## Completed

- Added a staged workflow navigation layer.
- Split the interface into Executive Dashboard, Recommendations, Review Pack, Action Plan and Raw Data views.
- Kept the dashboard and portfolio snapshot as the default landing view.
- Moved the 50-row recommendation table into its own view.
- Moved the raw industrial stream table into its own view so it no longer overwhelms the default screen.
- Made review-pack drill-down a focused view rather than another long section on the main page.
- Added a stronger review-pack summary with locked decision, risk, confidence and evidence cards.
- Added risk gates, assumptions and contract evidence sections to the visible review-pack layout.
- Improved domain-specific resource-efficiency prompts for grease trap waste, process water, waste heat, canteen organic streams, chemical residues, batteries, electronics, returnable containers and controlled textile/PPE-type streams.
- Improved supplier/contractor questions for controlled or hazardous streams so they request duty-of-care, treatment/recovery and acceptance evidence instead of generic recycled-content questions.

## Acceptance checks

- User can land on the Executive Dashboard without seeing all raw data at once.
- User can switch to Recommendations to filter and rank decision outputs.
- Clicking Review opens the Review Pack workflow view for the selected stream.
- User can switch to Action Plan without scrolling through the entire recommendation table.
- User can access Raw Data separately when needed.
- Grease trap waste no longer receives generic cutting-plan or batch-quality wording.
- The locked rules engine remains the source of truth.
- No backend recommendation logic, scoring logic or risk override behaviour is changed.

## Suggested commit message

```bash
git commit -m "style: add workflow layout and domain-specific review polish"
```
