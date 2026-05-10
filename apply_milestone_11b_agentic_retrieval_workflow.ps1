$ErrorActionPreference = "Stop"

Write-Host "Applying Milestone 11B: Agentic Retrieval Workflow" -ForegroundColor Cyan

function Backup-File($Path) {
    if (Test-Path $Path) {
        $backup = "$Path.bak-11b-$(Get-Date -Format yyyyMMddHHmmss)"
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

New-Item -ItemType Directory -Force -Path backend\app\agentic_retrieval | Out-Null
Copy-Item _milestone_11b_files\backend\app\agentic_retrieval\__init__.py backend\app\agentic_retrieval\__init__.py -Force
Copy-Item _milestone_11b_files\backend\app\agentic_retrieval\service.py backend\app\agentic_retrieval\service.py -Force
Copy-Item _milestone_11b_files\backend\app\routers\agentic_retrieval.py backend\app\routers\agentic_retrieval.py -Force
Copy-Item _milestone_11b_files\backend\tests\test_agentic_retrieval_workflow.py backend\tests\test_agentic_retrieval_workflow.py -Force
Copy-Item _milestone_11b_files\docs\milestone_11b_agentic_retrieval_workflow.md docs\milestone_11b_agentic_retrieval_workflow.md -Force

Backup-File "backend\app\schemas.py"
$schemaPatch = @'

# Milestone 11B: agentic retrieval workflow schemas

class AgenticRetrievalStep(BaseModel):
    step_id: str
    name: str
    status: str
    summary: str
    inputs: list[str]
    outputs: list[str]
    governance_note: str = ""


class AgenticRetrievalQualityGate(BaseModel):
    gate: str
    status: str
    detail: str


class AgenticRetrievalWorkflowResult(BaseModel):
    workflow_id: str
    workflow_name: str
    workflow_mode: str
    stream_id: str
    created_at: str
    save_insight: bool
    saved_insight_id: int | None = None
    stream_context: dict
    steps: list[AgenticRetrievalStep]
    quality_gates: list[AgenticRetrievalQualityGate]
    retrieval_summary: dict
    relationship_summary: dict
    graph: dict
    insight: dict
    governance_note: str
'@
Ensure-Contains "backend\app\schemas.py" "class AgenticRetrievalStep(BaseModel):" $schemaPatch

Backup-File "backend\app\main.py"
$main = Get-Content backend\app\main.py -Raw
if ($main -notmatch "agentic_retrieval") {
    $main = $main.Replace("knowledge, knowledge_graph, insights", "knowledge, knowledge_graph, agentic_retrieval, insights")
    $main = $main.Replace("app.include_router(knowledge_graph.router)`napp.include_router(insights.router)", "app.include_router(knowledge_graph.router)`napp.include_router(agentic_retrieval.router)`napp.include_router(insights.router)")
    Set-Content backend\app\main.py $main
    Write-Host "Patched: backend/app/main.py" -ForegroundColor Green
} else {
    Write-Host "Already patched: backend/app/main.py" -ForegroundColor Yellow
}

Write-Host "Milestone 11B applied." -ForegroundColor Green
Write-Host "Run backend pytest and frontend npm build before commit." -ForegroundColor Cyan
