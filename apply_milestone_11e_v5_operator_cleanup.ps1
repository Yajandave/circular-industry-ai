$ErrorActionPreference = "Stop"

Write-Host "Applying Milestone 11E v5: Operator wording and summary cleanup" -ForegroundColor Cyan

function Backup-File($Path) {
    if (Test-Path $Path) {
        $backup = "$Path.bak-11e-v5-$(Get-Date -Format yyyyMMddHHmmss)"
        Copy-Item $Path $backup
        Write-Host "Backup created: $backup" -ForegroundColor DarkGray
    }
}

Copy-Item _milestone_11e_v5_files\docs\milestone_11e_operator_usability_cleanup.md docs\milestone_11e_operator_usability_cleanup.md -Force

# Remove user-facing milestone/debug labels.
$labelFiles = @(
  "frontend\src\components\SiteAICopilotPanel.jsx",
  "frontend\src\components\AIReasoningPanel.jsx",
  "frontend\src\components\CircularActionReportPanel.jsx",
  "frontend\src\components\EvidenceRegister.jsx"
)

foreach ($file in $labelFiles) {
  Backup-File $file
  $text = Get-Content $file -Raw

  $text = $text.Replace('<span className="eyebrow">Milestone 8B</span>', '')
  $text = $text.Replace('<span className="eyebrow">Milestone 7C reasoning layer</span>', '')
  $text = $text.Replace('<span className="eyebrow">Milestone 8F</span>', '')
  $text = $text.Replace('<span className="eyebrow">Evidence workflow</span>', '')
  $text = $text.Replace('<span className="eyebrow">Evidence gap workflow</span>', '')

  $text = $text.Replace('Site-wide AI Copilot', 'Site-wide AI copilot')
  $text = $text.Replace('Rules-locked AI reasoning', 'Rules-locked reasoning assistant')
  $text = $text.Replace('Circular action report builder', 'Circular action report')
  $text = $text.Replace('Evidence register and gap explainer', 'Evidence register')

  Set-Content $file $text
  Write-Host "Cleaned labels: $file" -ForegroundColor Green
}

# Convert summary metric sections to robust operator summary cards.
$metricFiles = @(
  "frontend\src\components\CircularResolutionPlans.jsx",
  "frontend\src\components\SupplierLoopIntelligence.jsx",
  "frontend\src\components\MaterialPlaybooks.jsx",
  "frontend\src\components\EvidenceRegister.jsx"
)

foreach ($file in $metricFiles) {
  Backup-File $file
  $text = Get-Content $file -Raw

  $text = $text.Replace('className="resolution-summary-grid"', 'className="operator-summary-grid"')
  $text = $text.Replace('className="evidence-summary-grid"', 'className="operator-summary-grid"')
  $text = $text.Replace('className="metric-card"', 'className="operator-summary-card"')

  Set-Content $file $text
  Write-Host "Reframed summary cards: $file" -ForegroundColor Green
}

# Specific summary wording cleanup.
$path = "frontend\src\components\CircularResolutionPlans.jsx"
$text = Get-Content $path -Raw
$text = $text.Replace('>Export resolution plans CSV<', '>Export CSV<')
$text = $text.Replace('<span>Resolution plans</span>', '<span>Resolution register</span>')
$text = $text.Replace('<small>generated from locked recommendations</small>', '<small>screened intervention records</small>')
$text = $text.Replace('<span>Not claim-ready</span>', '<span>Claim-control cases</span>')
$text = $text.Replace('<small>blocked until evidence improves</small>', '<small>not claim-ready until evidence improves</small>')
Set-Content $path $text

$path = "frontend\src\components\SupplierLoopIntelligence.jsx"
$text = Get-Content $path -Raw
$text = $text.Replace('>Export supplier-loop CSV<', '>Export CSV<')
$text = $text.Replace('<span>Supplier-loop plans</span>', '<span>Supplier action register</span>')
$text = $text.Replace('<small>generated from locked recommendations</small>', '<small>evidence-controlled procurement records</small>')
$text = $text.Replace('<span className="eyebrow">Milestone 8D</span>', '')
Set-Content $path $text

$path = "frontend\src\components\MaterialPlaybooks.jsx"
$text = Get-Content $path -Raw
$text = $text.Replace('>Export playbooks CSV<', '>Export CSV<')
$text = $text.Replace('<span>Playbooks</span>', '<span>Material knowledge modules</span>')
$text = $text.Replace('<small>material-family knowledge modules</small>', '<small>playbooks for circular screening</small>')
Set-Content $path $text

# CSS for the new summary cards and hardening against glued text.
Backup-File "frontend\src\styles.css"
$styles = Get-Content frontend\src\styles.css -Raw
if ($styles -notmatch "Milestone 11E v5") {
    Add-Content frontend\src\styles.css @'

/* Milestone 11E v5: operator wording and summary cleanup */

.operator-summary-grid {
  display: grid !important;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin: 18px 0;
  width: 100%;
  max-width: 100%;
  min-width: 0;
}

.operator-summary-card {
  display: grid !important;
  grid-template-rows: auto auto 1fr;
  gap: 8px;
  min-width: 0;
  border: 1px solid #dfe7e2;
  border-radius: 20px;
  padding: 18px;
  background: #ffffff;
  box-shadow: 0 8px 22px rgba(36, 51, 44, 0.06);
  overflow: hidden;
}

.operator-summary-card span {
  display: block;
  color: #60716a;
  font-weight: 850;
  font-size: 0.82rem;
  line-height: 1.3;
  overflow-wrap: anywhere;
}

.operator-summary-card strong {
  display: block;
  color: #15231e;
  font-size: 1.7rem;
  letter-spacing: -0.03em;
  line-height: 1.05;
  white-space: normal;
  overflow-wrap: anywhere;
}

.operator-summary-card small {
  display: block;
  color: #66766e;
  line-height: 1.4;
  white-space: normal;
  overflow-wrap: anywhere;
}

/* Remove empty visual gaps if milestone eyebrow spans were removed. */
.section-heading .eyebrow:empty,
.ai-heading .eyebrow:empty {
  display: none;
}

/* Protect cards and panels from glued copied text / overflow. */
.section-heading,
.evidence-heading,
.ai-heading,
.copilot-status-grid,
.copilot-grid,
.action-report-lock-grid,
.action-report-section-grid,
.playbook-card-stack,
.supplier-loop-card-stack,
.resolution-card-stack {
  max-width: 100%;
  min-width: 0;
}

.section-heading h2,
.section-heading h3,
.section-heading p,
.operator-inspector h3,
.operator-inspector p,
.copilot-grid p,
.action-report-section-card p,
.material-playbook-card p,
.supplier-loop-card p,
.resolution-card p {
  overflow-wrap: anywhere;
}

/* Keep export controls visually separated from headings. */
.export-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
  justify-content: flex-end;
}

.export-actions a,
.export-actions button {
  min-width: 112px;
  justify-content: center;
  text-align: center;
}

/* Do not show development milestone labels as visual structure. */
.eyebrow {
  max-width: 100%;
  overflow-wrap: anywhere;
}
'@
    Write-Host "Patched: frontend/src/styles.css" -ForegroundColor Green
} else {
    Write-Host "Already patched: frontend/src/styles.css" -ForegroundColor Yellow
}

Write-Host "Milestone 11E v5 cleanup applied." -ForegroundColor Green
Write-Host "Run frontend build, backend tests and manual UI check before commit." -ForegroundColor Cyan
