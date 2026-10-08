"""Prepare a fresh, isolated synthetic demo database.

Never touches the application's default SQLite file. Every invocation creates
a new uniquely named database and intentionally excludes fake reviewers,
scenario outcomes and human challenges.
"""

from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import sys


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))
OUTPUT_DIR = Path(os.environ.get("CIRCULAR_DEMO_OUTPUT_DIR", str(BACKEND_DIR / "demo_databases"))).resolve()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
output = OUTPUT_DIR / f"governance_demo_{datetime.now(timezone.utc):%Y%m%d_%H%M%S_%f}.db"
if output.exists():
    raise SystemExit("Refusing to overwrite an existing demo database.")

database_url = f"sqlite:///{output.as_posix()}"
os.environ["DATABASE_URL"] = database_url

# Import only AFTER choosing the isolated database.
from app import crud, schemas  # noqa: E402
from app.database import SessionLocal, init_db  # noqa: E402
from app.rules_engine import recommend_for_streams  # noqa: E402
from app.utils.csv_loader import load_streams_from_csv  # noqa: E402

init_db()

with SessionLocal() as db:
    synthetic = load_streams_from_csv()
    count, _ = crud.replace_streams_with_audit_event(
        db,
        synthetic,
        event_type="dataset_loaded",
        entity_type="dataset",
        entity_id="synthetic_governance_demo",
        actor_type="system",
        actor_id="demo_preparation",
        source="demo_preparation_script",
        action="load_synthetic_demo_dataset",
        summary=f"Created a new isolated demo database with {len(synthetic)} synthetic streams.",
        decision_source="operator_demo_preparation",
        claim_boundary="This is synthetic example data, not measured site performance or external evidence.",
        metadata={"synthetic": True, "isolated_demo": True, "stream_count": len(synthetic)},
    )
    streams = crud.get_streams(db, limit=500)
    recommendations = [
        schemas.CircularRecommendationCreate(**rec.__dict__)
        for rec in recommend_for_streams(streams)
    ]
    recommendation_count, run_id = crud.persist_versioned_recommendation_run(
        db, streams=streams, recommendations=recommendations
    )

print("ISOLATED SYNTHETIC GOVERNANCE DEMO PREPARED")
print(f"Streams: {count} | Recommendations: {recommendation_count}")
print(f"Ruleset run: {run_id}")
print(f"Database file: {output}")
print("Use this exact environment setting in the backend PowerShell terminal:")
print(f'$env:DATABASE_URL = "{database_url}"')
print("Then start: uvicorn app.main:app --reload --port 8000")
print("No reviewer judgements, observed outcomes or decision challenges were created.")
