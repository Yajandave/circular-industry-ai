"""Versioned ruleset decision history regression tests."""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import pytest

from app.database import Base, get_db
from app.main import app
from app.ruleset_release import RULESET_VERSION


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def test_db():
        with TestingSession() as db:
            yield db

    app.dependency_overrides[get_db] = test_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_unversioned_legacy_records_not_backfilled(client):
    empty = client.get("/api/recommendations/history/S001")
    assert empty.status_code == 200
    assert empty.json()["records"] == []

    metadata = client.get("/api/recommendations/ruleset")
    assert metadata.status_code == 200
    assert metadata.json()["ruleset_version"] == RULESET_VERSION
    assert metadata.json()["rule_versions"]["R005_METAL_CLOSED_LOOP"] == "1.0.0"


def test_ruleset_run_snapshots_are_immutable_and_current_version_is_explicit(client):
    assert client.post("/api/streams/load-sample").status_code == 200
    first = client.post("/api/recommendations/run")
    assert first.status_code == 200
    assert first.json()["recommendations_created"] == 50

    history = client.get("/api/recommendations/history/S001").json()
    assert history["total_returned"] == 1
    snap = history["records"][0]
    assert snap["ruleset_version"] == RULESET_VERSION
    assert snap["rule_applied"] == "R005_METAL_CLOSED_LOOP"
    assert snap["rule_version"] == "1.0.0"
    assert snap["input_snapshot"]["stream_name"] == "Aluminium machining offcuts"
    assert snap["decision_snapshot"]["stream_id"] == "S001"
    assert snap["provenance_snapshot"]["provenance_status"] == "internal_material_screening_rule"

    pack = client.get("/api/agent/review-pack/S001").json()
    assert pack["ruleset_snapshot"]["record_status"] == "versioned_current_decision"
    assert pack["ruleset_snapshot"]["ruleset_version"] == RULESET_VERSION
    assert pack["ruleset_snapshot"]["run_id"] == snap["run_id"]

    second = client.post("/api/recommendations/run")
    assert second.status_code == 200
    history2 = client.get("/api/recommendations/history/S001").json()
    assert history2["total_returned"] == 2
    assert history2["records"][0]["run_id"] != history2["records"][1]["run_id"]
    assert history2["records"][1] == snap
    assert client.get("/api/agent/review-pack/S001").json()["ruleset_snapshot"]["run_id"] == history2["records"][0]["run_id"]


def test_loaded_new_dataset_does_not_retroactively_label_current_legacy_recommendation(client):
    assert client.post("/api/streams/load-sample").status_code == 200
    assert client.post("/api/recommendations/run").status_code == 200
    assert client.get("/api/recommendations/history/S001").json()["total_returned"] == 1
    assert client.post("/api/streams/load-sample").status_code == 200
    # Current recommendation absent after sample replacement; historical snapshot remains.
    assert client.get("/api/recommendations/S001").status_code == 404
    assert client.get("/api/recommendations/history/S001").json()["total_returned"] == 1
