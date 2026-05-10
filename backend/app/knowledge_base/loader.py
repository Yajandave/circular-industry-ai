"""Knowledge-base loader and validator for Circular Industry AI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent / "data"

ALLOWED_MATURITY = {
    "available_now",
    "pilot_ready",
    "emerging",
    "research_stage",
    "not_recommended",
}

REQUIRED_COLLECTIONS = {
    "materials": ["knowledge_id", "knowledge_type", "material_family", "aliases", "available_now_routes", "evidence_required", "unsafe_claims", "source_references"],
    "circular_routes": ["knowledge_id", "knowledge_type", "route", "required_data", "required_evidence", "claim_boundary", "source_references"],
    "evidence_rules": ["knowledge_id", "knowledge_type", "rule_name", "unsafe_claims", "default_claim_boundary", "source_references"],
    "future_horizon": ["knowledge_id", "knowledge_type", "topic", "maturity", "confidence", "claim_boundary", "source_references"],
}


def load_json(path: Path) -> dict[str, Any]:
    """Load one JSON knowledge file."""
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def knowledge_files(collection: str) -> list[Path]:
    """Return all JSON files for a collection."""
    folder = DATA_DIR / collection
    if not folder.exists():
        return []
    return sorted(folder.glob("*.json"))


def load_source_registry() -> dict[str, Any]:
    """Load source registry."""
    return load_json(DATA_DIR / "sources" / "source_registry.json")


def source_ids() -> set[str]:
    """Return known source IDs."""
    registry = load_source_registry()
    return {source["source_id"] for source in registry.get("sources", [])}


def load_collection(collection: str) -> list[dict[str, Any]]:
    """Load all JSON entries for one knowledge collection."""
    return [load_json(path) for path in knowledge_files(collection)]


def validate_knowledge_base() -> dict[str, Any]:
    """Validate required knowledge files and return a summary."""
    issues: list[str] = []
    counts: dict[str, int] = {}
    known_sources = source_ids()

    for collection, required_fields in REQUIRED_COLLECTIONS.items():
        records = load_collection(collection)
        counts[collection] = len(records)

        if not records:
            issues.append(f"Collection has no records: {collection}")

        for record in records:
            knowledge_id = record.get("knowledge_id", "unknown")
            for field in required_fields:
                if field not in record:
                    issues.append(f"{knowledge_id} missing required field: {field}")

            for source_id in record.get("source_references", []):
                if source_id not in known_sources:
                    issues.append(f"{knowledge_id} references unknown source_id: {source_id}")

            if collection == "future_horizon":
                maturity = record.get("maturity")
                if maturity not in ALLOWED_MATURITY:
                    issues.append(f"{knowledge_id} has invalid maturity: {maturity}")
                if not record.get("do_not_claim"):
                    issues.append(f"{knowledge_id} missing do_not_claim boundaries")

            if collection == "materials":
                for route in record.get("future_watch_routes", []):
                    maturity = route.get("maturity")
                    if maturity not in ALLOWED_MATURITY:
                        issues.append(f"{knowledge_id} future route has invalid maturity: {maturity}")
                    if not route.get("claim_boundary"):
                        issues.append(f"{knowledge_id} future route missing claim boundary")

            if not record.get("unsafe_claims") and collection in {"materials", "evidence_rules"}:
                issues.append(f"{knowledge_id} should include unsafe_claims")

    return {
        "valid": not issues,
        "counts": counts,
        "source_count": len(known_sources),
        "issues": issues,
        "governance_note": "Knowledge-base validation checks structure and source references. It does not verify site-specific compliance or operational impact.",
    }
