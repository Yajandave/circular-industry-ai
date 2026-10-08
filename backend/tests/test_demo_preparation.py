"""Smoke-test the isolated synthetic demo preparer without touching normal data."""

from __future__ import annotations

import os
from pathlib import Path
import sqlite3
import subprocess
import sys


def test_demo_preparer_creates_only_synthetic_versioned_data(tmp_path):
    backend_dir = Path(__file__).resolve().parents[1]
    script = backend_dir / "scripts" / "prepare_governance_demo.py"
    env = dict(os.environ)
    env["CIRCULAR_DEMO_OUTPUT_DIR"] = str(tmp_path)
    env["DATABASE_URL"] = "sqlite:///should_not_be_used_by_demo.db"

    process = subprocess.run(
        [sys.executable, str(script)],
        cwd=backend_dir,
        env=env,
        capture_output=True,
        text=True,
        timeout=45,
        check=False,
    )
    assert process.returncode == 0, process.stderr
    assert "ISOLATED SYNTHETIC GOVERNANCE DEMO PREPARED" in process.stdout
    assert "No reviewer judgements" in process.stdout

    dbs = list(tmp_path.glob("governance_demo_*.db"))
    assert len(dbs) == 1
    with sqlite3.connect(dbs[0]) as db:
        for table in (
            "industrial_streams",
            "circular_recommendations",
            "rule_decision_snapshots",
        ):
            assert db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 50
        for table in (
            "blind_decision_review_submissions",
            "observed_scenario_outcomes",
            "decision_challenges",
        ):
            assert db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0

        versions = db.execute(
            "SELECT DISTINCT ruleset_version FROM rule_decision_snapshots"
        ).fetchall()
        assert versions == [("circular-core-ruleset-v1.0.0",)]
