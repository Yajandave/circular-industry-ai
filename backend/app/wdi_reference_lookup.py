"""Read-only lookup of an operator-supplied, local WDI reference catalogue.

Data is intentionally NOT bundled in the public repository. The caller supplies
a local approved CSV path through WDI_REFERENCE_CATALOG_CSV. Never emits a
circular route, legal classification, or verified technical material property.
"""
from __future__ import annotations

import csv
import os
import re
from pathlib import Path

_CODE = re.compile(r"^\\d{2}\\s?\\d{2}\\s?\\d{2}\\*?$")
_REQUIRED = {"waste_code", "reported_description"}

def _normalise(code: str) -> str:
    return re.sub(r"\\s+", "", str(code or "")).upper()

def lookup_reported_waste_code(code: str, catalog_path: str | None = None) -> dict:
    requested = str(code or "").strip()
    if not _CODE.fullmatch(requested):
        return {"status": "invalid_code", "waste_code": requested, "matches": [], "message": "Expected a reported six-digit waste code, optionally with an asterisk."}
    path = catalog_path if catalog_path is not None else os.environ.get("WDI_REFERENCE_CATALOG_CSV")
    if not path:
        return {"status": "catalog_not_configured", "waste_code": requested, "matches": [], "message": "Configure a locally authorised reference catalogue."}
    file = Path(path)
    if not file.is_file():
        return {"status": "catalog_unavailable", "waste_code": requested, "matches": [], "message": "Configured local reference catalogue is unavailable."}
    matches = []
    with file.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if not _REQUIRED.issubset(reader.fieldnames or []):
            return {"status": "invalid_catalog_schema", "waste_code": requested, "matches": [], "message": "Reference catalogue is missing required code/description fields."}
        for row in reader:
            if _normalise(row.get("waste_code")) == _normalise(requested):
                matches.append({
                    "reported_description": row.get("reported_description"),
                    "reported_forms": row.get("reported_forms"),
                    "reported_basic_categories": row.get("reported_basic_categories"),
                    "reported_r_d_codes": row.get("reported_r_d_codes"),
                    "reported_fates": row.get("reported_fates"),
                    "source_scope": row.get("source_scope"),
                })
    return {
        "status": "found" if matches else "not_found",
        "waste_code": requested,
        "matches": matches,
        "verified_material_family": None,
        "recommended_circular_route": None,
        "decision_eligible": False,
        "governance_note": "Reported reference metadata only. No independent hazard classification, material grade or route suitability is verified.",
    }
