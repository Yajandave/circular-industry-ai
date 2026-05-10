param(
    [switch]$Force
)

Write-Host "Applying Milestone 10E: Insight History, Persistence and Traceability" -ForegroundColor Cyan

$ErrorActionPreference = "Stop"

function Backup-File($Path) {
    if (Test-Path $Path) {
        $backup = "$Path.bak-10e-$(Get-Date -Format yyyyMMddHHmmss)"
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

New-Item -ItemType Directory -Force -Path backend\app\insight_history | Out-Null
Copy-Item _milestone_10e_files\backend\app\insight_history\__init__.py backend\app\insight_history\__init__.py -Force
Copy-Item _milestone_10e_files\backend\app\insight_history\service.py backend\app\insight_history\service.py -Force
Copy-Item _milestone_10e_files\backend\app\routers\insights.py backend\app\routers\insights.py -Force
Copy-Item _milestone_10e_files\backend\tests\test_insight_history_traceability.py backend\tests\test_insight_history_traceability.py -Force
Copy-Item _milestone_10e_files\docs\milestone_10e_insight_history_traceability.md docs\milestone_10e_insight_history_traceability.md -Force

# Patch models.py
Backup-File "backend\app\models.py"
$generatedInsightModel = @'

# Milestone 10E: generated insight history and traceability

class GeneratedInsight(Base):
    """Persisted autonomous insight record for audit and history."""

    __tablename__ = "generated_insights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    stream_id: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    stream_name: Mapped[str] = mapped_column(String(255), nullable=False)
    material: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    source_process: Mapped[str] = mapped_column(String(160), nullable=False)
    analysis_run_id: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)

    input_snapshot_json: Mapped[str] = mapped_column(Text, nullable=False)
    matched_material_families_json: Mapped[str] = mapped_column(Text, nullable=False)
    current_action_json: Mapped[str] = mapped_column(Text, nullable=False)
    near_future_action_json: Mapped[str] = mapped_column(Text, nullable=False)
    future_watch_json: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_needed_json: Mapped[str] = mapped_column(Text, nullable=False)
    supplier_questions_json: Mapped[str] = mapped_column(Text, nullable=False)
    human_review_triggers_json: Mapped[str] = mapped_column(Text, nullable=False)
    do_not_claim_json: Mapped[str] = mapped_column(Text, nullable=False)
    source_knowledge_ids_json: Mapped[str] = mapped_column(Text, nullable=False)
    retrieval_notes_json: Mapped[str] = mapped_column(Text, nullable=False)

    input_notes_present: Mapped[bool] = mapped_column(nullable=False, default=False)
    notes_dependency: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    insight_summary: Mapped[str] = mapped_column(Text, nullable=False)
    claim_boundary: Mapped[str] = mapped_column(Text, nullable=False)
    generation_mode: Mapped[str] = mapped_column(String(80), index=True, nullable=False, default="deterministic")
    governance_note: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
'@
Ensure-Contains "backend\app\models.py" "class GeneratedInsight(Base):" $generatedInsightModel

# Patch schemas.py
Backup-File "backend\app\schemas.py"
$generatedInsightSchemas = @'

# Milestone 10E: generated insight history and traceability schemas

class GeneratedInsightRead(BaseModel):
    id: int
    stream_id: str
    stream_name: str
    material: str
    source_process: str
    analysis_run_id: int | None = None
    input_snapshot: dict
    input_notes_present: bool
    notes_dependency: str
    insight_summary: str
    matched_material_families: list[str]
    current_action: dict
    near_future_action: dict
    future_watch: dict
    evidence_needed: list[str]
    supplier_questions: list[str]
    human_review_triggers: list[str]
    do_not_claim: list[str]
    claim_boundary: str
    source_knowledge_ids: list[str]
    retrieval_notes: list[str]
    generation_mode: str
    governance_note: str
    created_at: datetime


class InsightHistorySummary(BaseModel):
    total_insights: int
    stream_count: int
    latest_insights: list[GeneratedInsightRead]
    governance_note: str
'@
Ensure-Contains "backend\app\schemas.py" "class GeneratedInsightRead(BaseModel):" $generatedInsightSchemas

# Patch crud.py
Backup-File "backend\app\crud.py"
$generatedInsightCrud = @'

# Milestone 10E: generated insight history CRUD helpers

def _json_dump(value) -> str:
    return json.dumps(value if value is not None else {}, ensure_ascii=False)


def _json_load(value: str, fallback):
    try:
        return json.loads(value or "")
    except (json.JSONDecodeError, TypeError):
        return fallback


def _generated_insight_read(row: models.GeneratedInsight) -> schemas.GeneratedInsightRead:
    return schemas.GeneratedInsightRead(
        id=row.id,
        stream_id=row.stream_id,
        stream_name=row.stream_name,
        material=row.material,
        source_process=row.source_process,
        analysis_run_id=row.analysis_run_id,
        input_snapshot=_json_load(row.input_snapshot_json, {}),
        input_notes_present=row.input_notes_present,
        notes_dependency=row.notes_dependency,
        insight_summary=row.insight_summary,
        matched_material_families=_json_load(row.matched_material_families_json, []),
        current_action=_json_load(row.current_action_json, {}),
        near_future_action=_json_load(row.near_future_action_json, {}),
        future_watch=_json_load(row.future_watch_json, {}),
        evidence_needed=_json_load(row.evidence_needed_json, []),
        supplier_questions=_json_load(row.supplier_questions_json, []),
        human_review_triggers=_json_load(row.human_review_triggers_json, []),
        do_not_claim=_json_load(row.do_not_claim_json, []),
        claim_boundary=row.claim_boundary,
        source_knowledge_ids=_json_load(row.source_knowledge_ids_json, []),
        retrieval_notes=_json_load(row.retrieval_notes_json, []),
        generation_mode=row.generation_mode,
        governance_note=row.governance_note,
        created_at=row.created_at,
    )


def create_generated_insight(
    db: Session,
    *,
    insight: dict,
    input_snapshot: dict,
    analysis_run_id: int | None = None,
    generation_mode: str = "deterministic",
) -> schemas.GeneratedInsightRead:
    """Persist one generated autonomous insight."""

    row = models.GeneratedInsight(
        stream_id=insight.get("stream_id") or "unknown",
        stream_name=insight.get("stream_name") or "",
        material=insight.get("material") or "",
        source_process=insight.get("source_process") or "",
        analysis_run_id=analysis_run_id,
        input_snapshot_json=_json_dump(input_snapshot),
        matched_material_families_json=_json_dump(insight.get("matched_material_families", [])),
        current_action_json=_json_dump(insight.get("current_action", {})),
        near_future_action_json=_json_dump(insight.get("near_future_action", {})),
        future_watch_json=_json_dump(insight.get("future_watch", {})),
        evidence_needed_json=_json_dump(insight.get("evidence_needed", [])),
        supplier_questions_json=_json_dump(insight.get("supplier_questions", [])),
        human_review_triggers_json=_json_dump(insight.get("human_review_triggers", [])),
        do_not_claim_json=_json_dump(insight.get("do_not_claim", [])),
        source_knowledge_ids_json=_json_dump(insight.get("source_knowledge_ids", [])),
        retrieval_notes_json=_json_dump(insight.get("retrieval_notes", [])),
        input_notes_present=bool(insight.get("input_notes_present", False)),
        notes_dependency=insight.get("notes_dependency", "unknown"),
        insight_summary=insight.get("insight_summary", ""),
        claim_boundary=insight.get("claim_boundary", ""),
        generation_mode=generation_mode,
        governance_note=insight.get("governance_note", ""),
    )

    db.add(row)
    db.commit()
    db.refresh(row)
    return _generated_insight_read(row)


def get_generated_insights(
    db: Session,
    *,
    limit: int = 100,
) -> list[schemas.GeneratedInsightRead]:
    query = (
        select(models.GeneratedInsight)
        .order_by(models.GeneratedInsight.created_at.desc(), models.GeneratedInsight.id.desc())
        .limit(limit)
    )
    return [_generated_insight_read(row) for row in db.scalars(query).all()]


def get_generated_insights_by_stream_id(
    db: Session,
    *,
    stream_id: str,
    limit: int = 50,
) -> list[schemas.GeneratedInsightRead]:
    query = (
        select(models.GeneratedInsight)
        .where(models.GeneratedInsight.stream_id == stream_id)
        .order_by(models.GeneratedInsight.created_at.desc(), models.GeneratedInsight.id.desc())
        .limit(limit)
    )
    return [_generated_insight_read(row) for row in db.scalars(query).all()]


def get_latest_generated_insight_by_stream_id(
    db: Session,
    *,
    stream_id: str,
) -> schemas.GeneratedInsightRead | None:
    query = (
        select(models.GeneratedInsight)
        .where(models.GeneratedInsight.stream_id == stream_id)
        .order_by(models.GeneratedInsight.created_at.desc(), models.GeneratedInsight.id.desc())
        .limit(1)
    )
    row = db.scalars(query).first()
    return _generated_insight_read(row) if row else None
'@
Ensure-Contains "backend\app\crud.py" "def create_generated_insight(" $generatedInsightCrud

Write-Host "Milestone 10E applied." -ForegroundColor Green
Write-Host "Run backend pytest and frontend npm build before commit." -ForegroundColor Cyan
