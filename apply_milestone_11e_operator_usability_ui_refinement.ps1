$ErrorActionPreference = "Stop"

Write-Host "Applying Milestone 11E v4: Professional Operator Master-Detail Layout" -ForegroundColor Cyan

function Backup-File($Path) {
    if (Test-Path $Path) {
        $backup = "$Path.bak-11e-v4-$(Get-Date -Format yyyyMMddHHmmss)"
        Copy-Item $Path $backup
        Write-Host "Backup created: $backup" -ForegroundColor DarkGray
    }
}

New-Item -ItemType Directory -Force -Path frontend\src\components | Out-Null
Copy-Item _milestone_11e_files\frontend\src\components\AIRuntimeStatus.jsx frontend\src\components\AIRuntimeStatus.jsx -Force
Copy-Item _milestone_11e_files\frontend\src\components\WorkflowNav.jsx frontend\src\components\WorkflowNav.jsx -Force
Copy-Item _milestone_11e_files\frontend\src\components\RecommendationsTable.jsx frontend\src\components\RecommendationsTable.jsx -Force
Copy-Item _milestone_11e_files\frontend\src\components\EvidenceRegister.jsx frontend\src\components\EvidenceRegister.jsx -Force
Copy-Item _milestone_11e_files\docs\milestone_11e_operator_usability_ui_refinement.md docs\milestone_11e_operator_usability_ui_refinement.md -Force

Backup-File "frontend\src\styles.css"
$styles = Get-Content frontend\src\styles.css -Raw
if ($styles -notmatch "Milestone 11E v4") {
    Add-Content frontend\src\styles.css @'

/* Milestone 11E v4: professional operator master-detail layout */

html,
body,
#root {
  max-width: 100%;
  overflow-x: hidden;
}

main,
section,
.workflow-shell,
.workflow-panel,
.dashboard-shell,
.table-card,
.section-card,
.evidence-register-section,
.recommendation-section,
.portfolio-snapshot,
.ai-runtime-status {
  max-width: 100%;
  min-width: 0;
}

button,
.link-button,
.secondary-button,
.file-button {
  white-space: nowrap;
  word-break: keep-all;
  overflow-wrap: normal;
  text-decoration: none;
}

/* Compact workflow navigation */
.operator-workflow-shell {
  overflow: hidden;
}

.compact-workflow-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.compact-workflow-tab {
  min-height: 0 !important;
  width: auto;
  min-width: 126px;
  max-width: 190px;
  padding: 10px 13px !important;
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.compact-workflow-tab strong {
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.compact-workflow-tab small {
  display: none !important;
}

/* Operator runtime */
.operator-runtime {
  padding: 20px;
}

.operator-runtime-main {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.operator-runtime-main h3 {
  margin: 4px 0 8px;
}

.operator-runtime-main p {
  margin: 0;
  color: #42524b;
  line-height: 1.55;
}

.runtime-mode-pill {
  display: inline-flex;
  width: fit-content;
  border-radius: 999px;
  padding: 8px 11px;
  font-size: 0.78rem;
  font-weight: 900;
  white-space: nowrap;
}

.runtime-mode-pill.on {
  background: #e4f4eb;
  color: #15613d;
}

.runtime-mode-pill.deterministic {
  background: #eef3ef;
  color: #25513f;
}

.runtime-diagnostics {
  margin-top: 14px;
  border-radius: 16px;
  border: 1px solid #dfe7e2;
  background: #fbfdfb;
  padding: 12px 14px;
}

.runtime-diagnostics summary {
  cursor: pointer;
  font-weight: 900;
  color: #1f5b43;
}

.runtime-diagnostics .ai-runtime-grid {
  margin-top: 12px;
}

/* Master-detail layout */
.operator-master-detail-section {
  overflow: hidden;
}

.operator-master-detail {
  display: grid;
  grid-template-columns: minmax(300px, 0.9fr) minmax(520px, 1.4fr);
  gap: 18px;
  align-items: stretch;
}

.operator-list-panel,
.operator-inspector {
  border: 1px solid #dfe7e2;
  border-radius: 22px;
  background: #ffffff;
  min-width: 0;
  overflow: hidden;
}

.operator-list-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 14px 16px;
  background: #f4f7f5;
  border-bottom: 1px solid #dfe7e2;
}

.operator-list-header small {
  color: #60716a;
  line-height: 1.35;
}

.operator-list-scroll {
  max-height: 640px;
  overflow-y: auto;
  padding: 8px;
}

.operator-list-row {
  width: 100%;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  text-align: left;
  background: #ffffff;
  color: #24332e;
  box-shadow: none;
  border: 1px solid transparent;
  border-radius: 16px;
  padding: 12px;
  margin: 0 0 8px;
}

.operator-list-row:hover {
  border-color: #cbdcd3;
  background: #f7faf8;
}

.operator-list-row.selected {
  border-color: #1f5b43;
  background: #ecf6f0;
}

.operator-row-main {
  min-width: 0;
}

.operator-row-main strong {
  display: block;
  margin: 4px 0;
  line-height: 1.25;
  white-space: normal;
  overflow-wrap: anywhere;
}

.operator-row-main small {
  display: block;
  color: #60716a;
  line-height: 1.35;
  white-space: normal;
  overflow-wrap: anywhere;
}

.operator-row-meta {
  display: flex;
  flex-direction: column;
  gap: 7px;
  align-items: flex-end;
  white-space: nowrap;
  font-weight: 800;
  color: #1f5b43;
}

.operator-row-meta small {
  color: #60716a;
}

.record-id {
  color: #4d5f57;
  font-size: 0.76rem;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.operator-inspector {
  padding: 20px;
}

.operator-inspector.empty {
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: #60716a;
}

.operator-inspector-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 16px;
}

.operator-inspector-header h3 {
  margin: 5px 0 6px;
  line-height: 1.25;
  overflow-wrap: anywhere;
}

.operator-inspector-header p {
  margin: 0;
  color: #60716a;
  line-height: 1.4;
}

.table-action-button,
.evidence-explain-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 128px;
  max-width: 100%;
  text-align: center;
  white-space: nowrap;
}

.evidence-explain-button {
  min-width: 178px;
}

.inspector-decision-box,
.operator-detail-section {
  border-radius: 18px;
  background: #f4f7f5;
  border: 1px solid #dfe7e2;
  padding: 15px;
  margin-bottom: 14px;
  min-width: 0;
}

.inspector-decision-box span,
.operator-detail-section span,
.inspector-kpi-grid article > span {
  display: block;
  color: #60716a;
  font-weight: 850;
  font-size: 0.78rem;
  margin-bottom: 7px;
}

.inspector-decision-box strong,
.operator-detail-section strong {
  display: block;
  line-height: 1.35;
  overflow-wrap: anywhere;
}

.inspector-decision-box p,
.operator-detail-section p {
  margin: 6px 0 0;
  line-height: 1.5;
  color: #33443d;
  overflow-wrap: anywhere;
}

.inspector-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 14px;
}

.inspector-kpi-grid article {
  border-radius: 16px;
  background: #ffffff;
  border: 1px solid #dfe7e2;
  padding: 13px;
  min-width: 0;
}

.inspector-kpi-grid strong {
  display: block;
  overflow-wrap: anywhere;
}

.inspector-kpi-grid small {
  display: block;
  margin-top: 5px;
  color: #66766e;
  line-height: 1.35;
}

.warning-detail {
  background: #fff8e8;
  border-color: #eed9a7;
}

/* Keep existing wide tables bounded if still used elsewhere. */
.table-wrap,
.evidence-table-wrap,
.recommendations-table-wrap {
  max-width: 100%;
  overflow: auto;
  max-height: 70vh;
}

/* Generic containment */
.metric-card,
.summary-card,
.snapshot-metric,
.evidence-breakdown-card,
.evidence-governance-note,
.evidence-priority-box,
.resolution-card,
.supplier-loop-card,
.agentic-step-card,
.agentic-gate-card,
.agentic-insight-grid article {
  min-width: 0;
  overflow-wrap: anywhere;
}

.export-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
}

@media (max-width: 1200px) {
  .operator-master-detail {
    grid-template-columns: 1fr;
  }

  .operator-list-scroll {
    max-height: 420px;
  }
}

@media (max-width: 760px) {
  .operator-runtime-main,
  .operator-inspector-header {
    flex-direction: column;
  }

  .inspector-kpi-grid {
    grid-template-columns: 1fr;
  }

  .operator-list-row {
    grid-template-columns: 1fr;
  }

  .operator-row-meta {
    align-items: flex-start;
  }

  .compact-workflow-tab {
    max-width: none;
    flex: 1 1 140px;
  }
}
'@
    Write-Host "Patched: frontend/src/styles.css" -ForegroundColor Green
} else {
    Write-Host "Already patched: frontend/src/styles.css" -ForegroundColor Yellow
}

Write-Host "Milestone 11E v4 applied." -ForegroundColor Green
Write-Host "Run backend pytest, frontend build and browser smoke test before commit." -ForegroundColor Cyan
