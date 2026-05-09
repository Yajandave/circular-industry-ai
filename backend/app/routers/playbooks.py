"""Material-specific circular economy playbook endpoints."""

from __future__ import annotations

import csv
from io import StringIO
from typing import Iterable

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app import schemas
from app.circular_resolution.advanced_playbooks import (
    build_playbook_summary,
    get_advanced_playbook_dict,
    list_advanced_playbooks,
)

router = APIRouter(prefix="/api", tags=["material circular playbooks"])


def _csv_response(rows: Iterable[dict], filename: str) -> StreamingResponse:
    rows = list(rows)
    buffer = StringIO()
    if rows:
        flattened = []
        for row in rows:
            flat = {key: "; ".join(value) if isinstance(value, list) else value for key, value in row.items()}
            flattened.append(flat)
        writer = csv.DictWriter(buffer, fieldnames=list(flattened[0].keys()))
        writer.writeheader()
        writer.writerows(flattened)
    buffer.seek(0)
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(iter([buffer.getvalue()]), media_type="text/csv", headers=headers)


@router.get("/playbooks", response_model=list[schemas.AdvancedMaterialPlaybook])
def list_material_playbooks():
    """Return material-specific circular economy playbooks."""
    return list_advanced_playbooks()


@router.get("/playbooks/summary", response_model=schemas.MaterialPlaybookSummary)
def material_playbook_summary():
    """Return a concise summary of material playbook coverage."""
    return build_playbook_summary()


@router.get("/playbooks/{material_family}", response_model=schemas.AdvancedMaterialPlaybook)
def get_material_playbook(material_family: str):
    """Return one material playbook by material family or material-like keyword."""
    try:
        return get_advanced_playbook_dict(material_family)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"No playbook found for {material_family}.") from exc


@router.get("/export/material-playbooks.csv")
def export_material_playbooks():
    """Export material playbooks as CSV."""
    return _csv_response(list_advanced_playbooks(), "circular-industry-ai-material-playbooks.csv")
