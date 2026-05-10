$ErrorActionPreference = "Stop"

Write-Host "Applying Milestone 11A: Knowledge Graph Relationship Layer" -ForegroundColor Cyan

function Backup-File($Path) {
    if (Test-Path $Path) {
        $backup = "$Path.bak-11a-$(Get-Date -Format yyyyMMddHHmmss)"
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

New-Item -ItemType Directory -Force -Path backend\app\knowledge_graph | Out-Null
Copy-Item _milestone_11a_files\backend\app\knowledge_graph\__init__.py backend\app\knowledge_graph\__init__.py -Force
Copy-Item _milestone_11a_files\backend\app\knowledge_graph\service.py backend\app\knowledge_graph\service.py -Force
Copy-Item _milestone_11a_files\backend\app\routers\knowledge_graph.py backend\app\routers\knowledge_graph.py -Force
Copy-Item _milestone_11a_files\backend\tests\test_knowledge_graph_relationships.py backend\tests\test_knowledge_graph_relationships.py -Force
Copy-Item _milestone_11a_files\docs\milestone_11a_knowledge_graph_relationship_layer.md docs\milestone_11a_knowledge_graph_relationship_layer.md -Force

Backup-File "backend\app\schemas.py"
$schemaPatch = @'

# Milestone 11A: knowledge graph relationship schemas

class KnowledgeGraphNode(BaseModel):
    node_id: str
    label: str
    node_type: str
    detail: str = ""
    source_knowledge_id: str | None = None


class KnowledgeGraphEdge(BaseModel):
    source: str
    target: str
    relationship: str
    evidence_level: str
    governance_note: str = ""


class KnowledgeGraphResult(BaseModel):
    graph_scope: str
    stream_id: str | None = None
    nodes: list[KnowledgeGraphNode]
    edges: list[KnowledgeGraphEdge]
    graph_path: list[str]
    matched_material_families: list[str]
    source_knowledge_ids: list[str]
    retrieval_notes: list[str]
    knowledge_validation: dict
    governance_note: str
'@
Ensure-Contains "backend\app\schemas.py" "class KnowledgeGraphNode(BaseModel):" $schemaPatch

Backup-File "backend\app\main.py"
$main = Get-Content backend\app\main.py -Raw
if ($main -notmatch "knowledge_graph") {
    $main = $main.Replace("knowledge, insights", "knowledge, knowledge_graph, insights")
    $main = $main.Replace("app.include_router(knowledge.router)`napp.include_router(insights.router)", "app.include_router(knowledge.router)`napp.include_router(knowledge_graph.router)`napp.include_router(insights.router)")
    Set-Content backend\app\main.py $main
    Write-Host "Patched: backend/app/main.py" -ForegroundColor Green
} else {
    Write-Host "Already patched: backend/app/main.py" -ForegroundColor Yellow
}

Write-Host "Milestone 11A applied." -ForegroundColor Green
Write-Host "Run backend pytest and frontend npm build before commit." -ForegroundColor Cyan
