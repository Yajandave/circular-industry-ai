$ErrorActionPreference = "Stop"

Write-Host "Applying Milestone 11C: Retrieval and Insight Quality Evaluation" -ForegroundColor Cyan

function Backup-File($Path) {
    if (Test-Path $Path) {
        $backup = "$Path.bak-11c-$(Get-Date -Format yyyyMMddHHmmss)"
        Copy-Item $Path $backup
        Write-Host "Backup created: $backup" -ForegroundColor DarkGray
    }
}

function Ensure-Contains($Path, $Needle, $AppendText) {
    $text = Get-Content $Path -Raw
    if ($text.Contains($Needle)) {
        Write-Host "Already patched: $Path contains $Needle" -ForegroundColor Yellow
        return
    }
    Add-Content -Path $Path -Value "`n$AppendText"
    Write-Host "Patched: $Path" -ForegroundColor Green
}

New-Item -ItemType Directory -Force -Path backend\app\evaluation | Out-Null
Copy-Item _milestone_11c_files\backend\app\evaluation\__init__.py backend\app\evaluation\__init__.py -Force
Copy-Item _milestone_11c_files\backend\app\evaluation\service.py backend\app\evaluation\service.py -Force
Copy-Item _milestone_11c_files\backend\app\routers\evaluation.py backend\app\routers\evaluation.py -Force
Copy-Item _milestone_11c_files\backend\tests\test_retrieval_insight_evaluation.py backend\tests\test_retrieval_insight_evaluation.py -Force
Copy-Item _milestone_11c_files\docs\milestone_11c_retrieval_insight_quality_evaluation.md docs\milestone_11c_retrieval_insight_quality_evaluation.md -Force

Backup-File "backend\app\schemas.py"
$schemaPatch = @'

# Milestone 11C: retrieval and insight quality evaluation schemas

class EvaluationCaseDefinition(BaseModel):
    case_id: str
    title: str
    description: str
    stream: dict
    expectations: dict


class EvaluationRunRequest(BaseModel):
    case_ids: list[str] | None = None


class EvaluationCheckResult(BaseModel):
    check_id: str
    status: str
    expected: object
    actual: object
    detail: str


class EvaluationCaseResult(BaseModel):
    case_id: str
    title: str
    status: str
    checks: list[EvaluationCheckResult]
    workflow_id: str
    matched_material_families: list[str]
    source_knowledge_ids: list[str]
    quality_gate_summary: dict
    governance_note: str


class EvaluationRunResult(BaseModel):
    suite_name: str
    overall_status: str
    total_cases: int
    status_breakdown: dict
    failed_checks: int
    review_checks: int
    results: list[EvaluationCaseResult]
    governance_note: str
'@
Ensure-Contains "backend\app\schemas.py" "class EvaluationCaseDefinition(BaseModel):" $schemaPatch

Backup-File "backend\app\main.py"
$main = Get-Content backend\app\main.py -Raw
if ($main -notmatch "evaluation") {
    $main = $main.Replace("agentic_retrieval, insights", "agentic_retrieval, evaluation, insights")
    $main = $main.Replace("app.include_router(agentic_retrieval.router)`napp.include_router(insights.router)", "app.include_router(agentic_retrieval.router)`napp.include_router(evaluation.router)`napp.include_router(insights.router)")
    Set-Content backend\app\main.py $main
    Write-Host "Patched: backend/app/main.py" -ForegroundColor Green
} else {
    Write-Host "Already patched: backend/app/main.py" -ForegroundColor Yellow
}

Write-Host "Milestone 11C applied." -ForegroundColor Green
Write-Host "Run backend pytest and frontend npm build before commit." -ForegroundColor Cyan
