# Milestone 6B Acceptance Criteria

## Objective

Improve the Milestone 6 frontend so the product is easier to inspect, screenshot and export for portfolio use without weakening the industrial circular economy decision logic.

Milestone 6B is a presentation and usability patch. It does not alter the backend rules engine, recommendation scoring, evidence scoring, risk scoring or agentic controls.

## Completed

- [x] Added a portfolio snapshot section for recruiter-ready screenshots.
- [x] Added concise metrics for streams screened, review gates, screened value exposure and diversion potential.
- [x] Added priority validation and controlled-review examples.
- [x] Simplified the recommendations table layout by grouping related fields.
- [x] Reduced table width pressure and improved wrapping for long industrial actions.
- [x] Added print/PDF-specific CSS.
- [x] Hid interactive controls, filters and large raw tables in print view.
- [x] Improved hero title spacing for browser print export.
- [x] Preserved governance language that screening estimates are not verified savings or verified environmental benefit.

## Manual checks

1. Start the backend.
2. Start the frontend.
3. Load the sample dataset.
4. Run recommendations.
5. Confirm the dashboard, portfolio snapshot, recommendation table and action plan render.
6. Open browser print preview and confirm the output is concise and not clipped.
7. Open at least one agentic review pack to confirm Milestone 4 functionality still works.

## Suggested commit message

```text
style: polish dashboard UI for portfolio screenshots
```

## Recruiter-facing value

This polish milestone improves the project from a working technical interface into a portfolio-ready product presentation. It shows that the project owner understands not only backend logic and circular economy analysis, but also how to communicate decision-support outputs clearly to non-technical users.
