param(
  [switch]$NoBackup
)

$ErrorActionPreference = "Stop"
$repoRoot = Get-Location

$modelsPath = Join-Path $repoRoot "backend\app\models.py"
$schemasPath = Join-Path $repoRoot "backend\app\schemas.py"
$crudPath = Join-Path $repoRoot "backend\app\crud.py"
$mainPath = Join-Path $repoRoot "backend\app\main.py"

foreach ($path in @($modelsPath, $schemasPath, $crudPath, $mainPath)) {
  if (!(Test-Path $path)) {
    throw "Missing expected file: $path. Run this script from repo root after extracting the zip."
  }
}

if (!$NoBackup) {
  $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
  foreach ($path in @($modelsPath, $schemasPath, $crudPath, $mainPath)) {
    Copy-Item $path "$path.bak-$stamp"
  }
}

# 1. Append metadata models.
$models = Get-Content $modelsPath -Raw
if ($models -notmatch "class Organisation") {
  $modelAppend = @'


# Milestone 9D: product data-model foundation

class Organisation(Base):
    """Business organisation using the Circular Industry AI workflow."""

    __tablename__ = "organisations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organisation_name: Mapped[str] = mapped_column(String(160), unique=True, index=True, nullable=False)
    sector: Mapped[str] = mapped_column(String(120), nullable=False, default="manufacturing")
    region: Mapped[str] = mapped_column(String(120), nullable=False, default="unspecified")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Site(Base):
    """Operational site where material streams are reviewed."""

    __tablename__ = "sites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organisation_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    site_name: Mapped[str] = mapped_column(String(160), index=True, nullable=False)
    site_type: Mapped[str] = mapped_column(String(120), nullable=False, default="manufacturing")
    country: Mapped[str] = mapped_column(String(120), nullable=False, default="unspecified")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class AnalysisRun(Base):
    """Metadata snapshot of one product analysis run."""

    __tablename__ = "analysis_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organisation_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    site_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    run_name: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    run_status: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    decision_source: Mapped[str] = mapped_column(String(120), nullable=False)
    stream_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    recommendation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    human_review_required_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    low_risk_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    medium_risk_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    high_risk_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    blocked_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_estimated_annual_waste_diverted_kg: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    total_estimated_annual_disposal_cost_avoided: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    governance_note: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
'@
  Add-Content $modelsPath $modelAppend
}

# 2. Append schemas.
$schemas = Get-Content $schemasPath -Raw
if ($schemas -notmatch "class OrganisationRead") {
  $schemaAppend = @'


# Milestone 9D: product data-model foundation schemas

class OrganisationRead(BaseModel):
    id: int
    organisation_name: str
    sector: str
    region: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SiteRead(BaseModel):
    id: int
    organisation_id: int
    site_name: str
    site_type: str
    country: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalysisRunRead(BaseModel):
    id: int
    organisation_id: int
    site_id: int
    run_name: str
    run_status: str
    decision_source: str
    stream_count: int
    recommendation_count: int
    human_review_required_count: int
    low_risk_count: int
    medium_risk_count: int
    high_risk_count: int
    blocked_count: int
    total_estimated_annual_waste_diverted_kg: float
    total_estimated_annual_disposal_cost_avoided: float
    governance_note: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkspaceContext(BaseModel):
    organisation: OrganisationRead
    site: SiteRead
    latest_analysis_run: AnalysisRunRead | None = None
    stream_summary: StreamSummary
    recommendation_summary: RecommendationSummary
    data_model_stage: str
    governance_note: str
'@
  Add-Content $schemasPath $schemaAppend
}

# 3. Append CRUD helpers.
$crud = Get-Content $crudPath -Raw
if ($crud -notmatch "def ensure_default_workspace") {
  $crudAppend = @'


# Milestone 9D: product data-model foundation CRUD helpers

def ensure_default_workspace(db: Session) -> tuple[models.Organisation, models.Site]:
    """Ensure a default organisation and site exist for the current Alpha workflow."""
    organisation = db.scalars(
        select(models.Organisation).where(models.Organisation.organisation_name == "Default Organisation")
    ).first()

    if organisation is None:
        organisation = models.Organisation(
            organisation_name="Default Organisation",
            sector="manufacturing",
            region="unspecified",
        )
        db.add(organisation)
        db.commit()
        db.refresh(organisation)

    site = db.scalars(
        select(models.Site).where(
            models.Site.organisation_id == organisation.id,
            models.Site.site_name == "Default Manufacturing Site",
        )
    ).first()

    if site is None:
        site = models.Site(
            organisation_id=organisation.id,
            site_name="Default Manufacturing Site",
            site_type="manufacturing",
            country="unspecified",
        )
        db.add(site)
        db.commit()
        db.refresh(site)

    return organisation, site


def create_analysis_run_snapshot(
    db: Session,
    *,
    organisation_id: int,
    site_id: int,
) -> models.AnalysisRun:
    """Create a metadata snapshot of the current loaded streams and recommendations."""
    stream_summary = get_stream_summary(db)
    recommendation_summary = get_recommendation_summary(db)

    existing_count = db.scalar(
        select(func.count(models.AnalysisRun.id)).where(models.AnalysisRun.site_id == site_id)
    ) or 0

    snapshot = models.AnalysisRun(
        organisation_id=organisation_id,
        site_id=site_id,
        run_name=f"Analysis snapshot {existing_count + 1}",
        run_status="snapshot_created",
        decision_source="locked_rules_engine",
        stream_count=stream_summary.total_streams,
        recommendation_count=recommendation_summary.total_recommendations,
        human_review_required_count=recommendation_summary.human_review_required,
        low_risk_count=recommendation_summary.low_risk,
        medium_risk_count=recommendation_summary.medium_risk,
        high_risk_count=recommendation_summary.high_risk,
        blocked_count=recommendation_summary.blocked,
        total_estimated_annual_waste_diverted_kg=recommendation_summary.total_estimated_annual_waste_diverted_kg,
        total_estimated_annual_disposal_cost_avoided=recommendation_summary.total_estimated_annual_disposal_cost_avoided,
        governance_note=(
            "Analysis-run metadata is a snapshot of current Alpha workflow outputs. It does not verify "
            "legal compliance, supplier capability, carbon savings, financial savings or operational impact."
        ),
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


def get_latest_analysis_run(db: Session, *, site_id: int) -> models.AnalysisRun | None:
    query = (
        select(models.AnalysisRun)
        .where(models.AnalysisRun.site_id == site_id)
        .order_by(models.AnalysisRun.created_at.desc(), models.AnalysisRun.id.desc())
        .limit(1)
    )
    return db.scalars(query).first()


def get_analysis_runs(db: Session, *, site_id: int, limit: int = 50) -> list[models.AnalysisRun]:
    query = (
        select(models.AnalysisRun)
        .where(models.AnalysisRun.site_id == site_id)
        .order_by(models.AnalysisRun.created_at.desc(), models.AnalysisRun.id.desc())
        .limit(limit)
    )
    return list(db.scalars(query).all())
'@
  Add-Content $crudPath $crudAppend
}

# 4. Mount workspace router.
$lines = Get-Content $mainPath
$patchedLines = foreach ($line in $lines) {
  if ($line.StartsWith("from app.routers import ") -and $line -notmatch "(^|, )workspace(,|$)") {
    $prefix = "from app.routers import "
    $importsText = $line.Substring($prefix.Length)
    $imports = $importsText.Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ }
    $imports += "workspace"
    $imports = $imports | Select-Object -Unique
    "$prefix$($imports -join ', ')"
  } else {
    $line
  }
}

$main = $patchedLines -join [Environment]::NewLine

if ($main -notmatch "app\.include_router\(workspace\.router\)") {
  if ($main -match "app\.include_router\(diagnostics\.router\)") {
    $main = $main.Replace("app.include_router(diagnostics.router)", "app.include_router(diagnostics.router)`r`napp.include_router(workspace.router)")
  } else {
    $main += "`r`napp.include_router(workspace.router)`r`n"
  }
}

Set-Content $mainPath $main

Write-Host "Milestone 9D data model foundation patch applied."
Write-Host "Next: remove backups, run backend tests, frontend build, and workflow verification."
