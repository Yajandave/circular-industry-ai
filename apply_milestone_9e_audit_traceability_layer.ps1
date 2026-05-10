param(
  [switch]$NoBackup
)

$ErrorActionPreference = "Stop"
$repoRoot = Get-Location

$modelsPath = Join-Path $repoRoot "backend\app\models.py"
$schemasPath = Join-Path $repoRoot "backend\app\schemas.py"
$crudPath = Join-Path $repoRoot "backend\app\crud.py"
$mainPath = Join-Path $repoRoot "backend\app\main.py"
$streamsPath = Join-Path $repoRoot "backend\app\routers\streams.py"
$recommendationsPath = Join-Path $repoRoot "backend\app\routers\recommendations.py"
$workspacePath = Join-Path $repoRoot "backend\app\routers\workspace.py"

foreach ($path in @($modelsPath, $schemasPath, $crudPath, $mainPath, $streamsPath, $recommendationsPath, $workspacePath)) {
  if (!(Test-Path $path)) {
    throw "Missing expected file: $path. Run this script from repo root after extracting the zip."
  }
}

if (!$NoBackup) {
  $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
  foreach ($path in @($modelsPath, $schemasPath, $crudPath, $mainPath, $streamsPath, $recommendationsPath, $workspacePath)) {
    Copy-Item $path "$path.bak-$stamp"
  }
}

# 1. Append AuditEvent model.
$models = Get-Content $modelsPath -Raw
if ($models -notmatch "class AuditEvent") {
  $modelAppend = @'


# Milestone 9E: audit and traceability layer

class AuditEvent(Base):
    """Traceable product workflow event."""

    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_type: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    entity_type: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    entity_id: Mapped[str] = mapped_column(String(160), index=True, nullable=True)
    actor_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False, default="system")
    actor_id: Mapped[str] = mapped_column(String(160), nullable=True)
    source: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    action: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    decision_source: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    claim_boundary: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
'@
  Add-Content $modelsPath $modelAppend
}

# 2. Append audit schemas.
$schemas = Get-Content $schemasPath -Raw
if ($schemas -notmatch "class AuditEventCreate") {
  $schemaAppend = @'


# Milestone 9E: audit and traceability schemas

class AuditEventCreate(BaseModel):
    event_type: str
    entity_type: str
    entity_id: str | None = None
    actor_type: str = "system"
    actor_id: str | None = None
    source: str
    action: str
    summary: str
    decision_source: str
    claim_boundary: str
    metadata_json: dict = {}


class AuditEventRead(BaseModel):
    id: int
    event_type: str
    entity_type: str
    entity_id: str | None = None
    actor_type: str
    actor_id: str | None = None
    source: str
    action: str
    summary: str
    decision_source: str
    claim_boundary: str
    metadata_json: dict
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditSummary(BaseModel):
    total_events: int
    event_type_breakdown: dict
    entity_type_breakdown: dict
    decision_source_breakdown: dict
    latest_events: list[AuditEventRead]
    governance_note: str
'@
  Add-Content $schemasPath $schemaAppend
}

# 3. Append CRUD helpers.
$crud = Get-Content $crudPath -Raw
if ($crud -notmatch "import json") {
  $crud = $crud.Replace("from __future__ import annotations", "from __future__ import annotations`r`n`r`nimport json")
}

if ($crud -notmatch "def create_audit_event") {
  $crudAppend = @'


# Milestone 9E: audit and traceability CRUD helpers

def _audit_read(event: models.AuditEvent) -> schemas.AuditEventRead:
    """Convert an AuditEvent ORM row into a schema with parsed metadata."""
    try:
        metadata = json.loads(event.metadata_json or "{}")
    except json.JSONDecodeError:
        metadata = {"raw_metadata_json": event.metadata_json}

    return schemas.AuditEventRead(
        id=event.id,
        event_type=event.event_type,
        entity_type=event.entity_type,
        entity_id=event.entity_id,
        actor_type=event.actor_type,
        actor_id=event.actor_id,
        source=event.source,
        action=event.action,
        summary=event.summary,
        decision_source=event.decision_source,
        claim_boundary=event.claim_boundary,
        metadata_json=metadata,
        created_at=event.created_at,
    )


def create_audit_event(
    db: Session,
    *,
    event_type: str,
    entity_type: str,
    entity_id: str | None,
    actor_type: str = "system",
    actor_id: str | None = None,
    source: str,
    action: str,
    summary: str,
    decision_source: str,
    claim_boundary: str,
    metadata: dict | None = None,
) -> schemas.AuditEventRead:
    """Create and return a traceable audit event."""
    event = models.AuditEvent(
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        actor_type=actor_type,
        actor_id=actor_id,
        source=source,
        action=action,
        summary=summary,
        decision_source=decision_source,
        claim_boundary=claim_boundary,
        metadata_json=json.dumps(metadata or {}, ensure_ascii=False),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return _audit_read(event)


def get_audit_events(
    db: Session,
    *,
    event_type: str | None = None,
    entity_type: str | None = None,
    limit: int = 100,
) -> list[schemas.AuditEventRead]:
    query = select(models.AuditEvent).order_by(models.AuditEvent.created_at.desc(), models.AuditEvent.id.desc())

    if event_type:
        query = query.where(func.lower(models.AuditEvent.event_type) == event_type.lower())
    if entity_type:
        query = query.where(func.lower(models.AuditEvent.entity_type) == entity_type.lower())

    query = query.limit(limit)
    return [_audit_read(event) for event in db.scalars(query).all()]


def get_audit_summary(db: Session) -> schemas.AuditSummary:
    events = list(
        db.scalars(
            select(models.AuditEvent)
            .order_by(models.AuditEvent.created_at.desc(), models.AuditEvent.id.desc())
            .limit(500)
        ).all()
    )

    def breakdown(attribute: str) -> dict:
        result: dict[str, int] = {}
        for event in events:
            value = getattr(event, attribute) or "unknown"
            result[value] = result.get(value, 0) + 1
        return result

    return schemas.AuditSummary(
        total_events=len(events),
        event_type_breakdown=breakdown("event_type"),
        entity_type_breakdown=breakdown("entity_type"),
        decision_source_breakdown=breakdown("decision_source"),
        latest_events=[_audit_read(event) for event in events[:10]],
        governance_note=(
            "Audit events record workflow traceability. They do not independently verify legal compliance, "
            "supplier capability, carbon savings, financial savings or completed operational impact."
        ),
    )
'@
  $crud += $crudAppend
}

Set-Content $crudPath $crud

# 4. Mount audit router.
$lines = Get-Content $mainPath
$patchedLines = foreach ($line in $lines) {
  if ($line.StartsWith("from app.routers import ") -and $line -notmatch "(^|, )audit(,|$)") {
    $prefix = "from app.routers import "
    $importsText = $line.Substring($prefix.Length)
    $imports = $importsText.Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ }
    $imports += "audit"
    $imports = $imports | Select-Object -Unique
    "$prefix$($imports -join ', ')"
  } else {
    $line
  }
}
$main = $patchedLines -join [Environment]::NewLine
if ($main -notmatch "app\.include_router\(audit\.router\)") {
  if ($main -match "app\.include_router\(workspace\.router\)") {
    $main = $main.Replace("app.include_router(workspace.router)", "app.include_router(workspace.router)`r`napp.include_router(audit.router)")
  } elseif ($main -match "app\.include_router\(diagnostics\.router\)") {
    $main = $main.Replace("app.include_router(diagnostics.router)", "app.include_router(diagnostics.router)`r`napp.include_router(audit.router)")
  } else {
    $main += "`r`napp.include_router(audit.router)`r`n"
  }
}
Set-Content $mainPath $main

# 5. Patch stream data-load audit events.
$streams = Get-Content $streamsPath -Raw
if ($streams -notmatch "event_type=`"dataset_loaded`"") {
  $sampleAnchor = "    loaded_rows = crud.bulk_replace_streams(db, streams)"
  $sampleAudit = @'
    loaded_rows = crud.bulk_replace_streams(db, streams)
    crud.create_audit_event(
        db,
        event_type="dataset_loaded",
        entity_type="dataset",
        entity_id="sample",
        actor_type="operator",
        actor_id="local_user",
        source="streams_router",
        action="load_sample_dataset",
        summary=f"Loaded {loaded_rows} sample material streams and replaced existing stream/recommendation rows.",
        decision_source="operator_action",
        claim_boundary="Data loading does not create verified circular economy, cost or environmental impact claims.",
        metadata={"loaded_rows": loaded_rows, "replaced_existing_rows": True},
    )
'@
  $streams = $streams.Replace($sampleAnchor, $sampleAudit)

  $uploadAnchor = "    loaded_rows = crud.bulk_replace_streams(db, streams)"
  $uploadReplacement = @'
    loaded_rows = crud.bulk_replace_streams(db, streams)
    crud.create_audit_event(
        db,
        event_type="dataset_uploaded",
        entity_type="dataset",
        entity_id=file.filename,
        actor_type="operator",
        actor_id="local_user",
        source="streams_router",
        action="upload_csv_dataset",
        summary=f"Uploaded CSV '{file.filename}' with {loaded_rows} material streams and replaced existing stream/recommendation rows.",
        decision_source="operator_action",
        claim_boundary="CSV upload does not create verified circular economy, cost or environmental impact claims.",
        metadata={"loaded_rows": loaded_rows, "filename": file.filename, "replaced_existing_rows": True},
    )
'@
  # Replace the second occurrence only by using a temporary marker.
  $firstIndex = $streams.IndexOf($sampleAudit)
  $secondIndex = $streams.IndexOf($uploadAnchor, $firstIndex + $sampleAudit.Length)
  if ($secondIndex -ge 0) {
    $streams = $streams.Remove($secondIndex, $uploadAnchor.Length).Insert($secondIndex, $uploadReplacement)
  }
}
Set-Content $streamsPath $streams

# 6. Patch recommendations run audit event.
$recommendations = Get-Content $recommendationsPath -Raw
if ($recommendations -notmatch "event_type=`"rules_engine_run`"") {
  $anchor = "    created_count = crud.bulk_replace_recommendations(db, recommendations)"
  $replacement = @'
    created_count = crud.bulk_replace_recommendations(db, recommendations)
    crud.create_audit_event(
        db,
        event_type="rules_engine_run",
        entity_type="recommendation_run",
        entity_id="latest",
        actor_type="system",
        actor_id="rules_engine",
        source="recommendations_router",
        action="run_locked_rules_engine",
        summary=f"Generated {created_count} locked circular economy recommendations.",
        decision_source="locked_rules_engine",
        claim_boundary="Rules-engine outputs are screening recommendations, not verified circularity, cost or environmental impact claims.",
        metadata={
            "analysed_streams": len(streams),
            "recommendations_created": created_count,
        },
    )
'@
  $recommendations = $recommendations.Replace($anchor, $replacement)
}
Set-Content $recommendationsPath $recommendations

# 7. Patch workspace snapshot audit event.
$workspace = Get-Content $workspacePath -Raw
if ($workspace -notmatch "event_type=`"analysis_run_snapshot`"") {
  $anchor = "    return crud.create_analysis_run_snapshot(db, organisation_id=organisation.id, site_id=site.id)"
  $replacement = @'
    snapshot = crud.create_analysis_run_snapshot(db, organisation_id=organisation.id, site_id=site.id)
    crud.create_audit_event(
        db,
        event_type="analysis_run_snapshot",
        entity_type="analysis_run",
        entity_id=str(snapshot.id),
        actor_type="operator",
        actor_id="local_user",
        source="workspace_router",
        action="create_analysis_run_snapshot",
        summary=f"Created analysis-run metadata snapshot {snapshot.id} for the current workflow state.",
        decision_source="metadata_snapshot",
        claim_boundary="Analysis-run snapshot records current workflow outputs; it does not verify operational impact.",
        metadata={
            "analysis_run_id": snapshot.id,
            "stream_count": snapshot.stream_count,
            "recommendation_count": snapshot.recommendation_count,
            "human_review_required_count": snapshot.human_review_required_count,
        },
    )
    return snapshot
'@
  $workspace = $workspace.Replace($anchor, $replacement)
}
Set-Content $workspacePath $workspace

Write-Host "Milestone 9E audit and traceability layer patch applied."
Write-Host "Next: remove backups, run backend tests, frontend build, and workflow verification."
