"""Conservative material-family interpretation for operator-confirmed draft imports.

A description is not proof of grade, condition, contamination or legal waste status.
Matching only a narrow unambiguous material term is intentional.
"""
from __future__ import annotations

import re

FAMILIAR_LEGACY_LABELS = frozenset({"steel", "cardboard"})

CANONICAL_FAMILIES = frozenset({
    "metals", "plastics", "chemicals/solvents", "cardboard/packaging",
    "wood/pallets", "glass", "rubber", "textiles",
    "organic/process residue", "process mineral residue", "process water",
    "energy/resource stream", "electronic components",
})
PATTERNS = (
    ("metals", r"\b(?:aluminium|aluminum|stainless steel|steel|ferrous|copper|brass|bronze|metal|metals)\b"),
    ("plastics", r"\b(?:hdpe|ldpe|polyethylene|polypropylene|pet|pvc|plastic|plastics)\b"),
    ("chemicals/solvents", r"\b(?:acetone|solvent|solvents)\b"),
    ("wood/pallets", r"\b(?:wood|wooden pallets|timber|pallets)\b"),
    ("glass", r"\bglass\b"),
    ("rubber", r"\brubber\b"),
    ("textiles", r"\b(?:textile|textiles|fabric)\b"),
)
# Catch ambiguous mixed-material inputs without guessing a primary component.
AMBIGUOUS = re.compile(r"\b(?:mixed materials|mixed waste|composite|unknown|unspecified)\b", re.I)


def interpret_material_family(raw_material: str) -> dict[str, str | None]:
    original = str(raw_material or "").strip()
    normalised = original.casefold()
    if normalised in FAMILIAR_LEGACY_LABELS:
        return {"original": original, "proposed_family": None, "status": "familiar_legacy_label_unchanged"}
    if normalised in CANONICAL_FAMILIES:
        return {"original": original, "proposed_family": normalised, "status": "already_canonical"}
    if not original or AMBIGUOUS.search(normalised):
        return {"original": original, "proposed_family": None, "status": "unresolved"}
    hits = {family for family, pattern in PATTERNS if re.search(pattern, normalised, re.I)}
    if len(hits) == 1:
        return {"original": original, "proposed_family": next(iter(hits)), "status": "proposed_requires_operator_confirmation"}
    return {"original": original, "proposed_family": None, "status": "ambiguous_or_unrecognised"}
