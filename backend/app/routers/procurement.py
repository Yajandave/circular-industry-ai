"""Circular procurement and supplier-loop intelligence endpoints."""

from __future__ import annotations

import csv
from io import StringIO
from typing import Iterable

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.procurement.supplier_loop_engine import build_supplier_loop_plans, build_supplier_loop_summary

router = APIRouter(prefix="/api", tags=["circular procurement and supplier loops"])


def _require_supplier_loop_plans(db: Session) -> list[dict]:
    streams = crud.get_streams(db, limit=500)
    recommendations = crud.get_recommendations(db, limit=500)
    if not streams:
        raise HTTPException(status_code=404, detail="No streams found. Load a dataset first.")
    if not recommendations:
        raise HTTPException(status_code=404, detail="No recommendations found. Run POST /api/recommendations/run first.")
    return build_supplier_loop_plans(streams, recommendations)


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


@router.post("/procurement/run", response_model=schemas.RunSupplierLoopsResponse)
def run_supplier_loop_intelligence(db: Session = Depends(get_db)):
    """Generate supplier-loop plans from locked recommendations and resolution plans."""
    plans = _require_supplier_loop_plans(db)
    summary = build_supplier_loop_summary(plans)
    return schemas.RunSupplierLoopsResponse(
        generated_plans=summary["total_plans"],
        supplier_loop_candidates=summary["supplier_loop_candidates"],
        controlled_supplier_reviews=summary["controlled_supplier_reviews"],
        message="Supplier-loop and circular procurement plans generated from locked circular resolution outputs.",
    )


@router.get("/procurement/supplier-loops", response_model=list[schemas.SupplierLoopPlan])
def list_supplier_loop_plans(db: Session = Depends(get_db)):
    """Return supplier-loop and circular procurement plans for all recommendations."""
    return _require_supplier_loop_plans(db)


@router.get("/procurement/supplier-loops/summary", response_model=schemas.SupplierLoopSummary)
def supplier_loop_summary(db: Session = Depends(get_db)):
    """Return summary metrics for supplier-loop opportunities and review controls."""
    return build_supplier_loop_summary(_require_supplier_loop_plans(db))


@router.get("/procurement/supplier-loops/{stream_id}", response_model=schemas.SupplierLoopPlan)
def get_supplier_loop_plan(stream_id: str, db: Session = Depends(get_db)):
    """Return one supplier-loop plan by stream ID."""
    for plan in _require_supplier_loop_plans(db):
        if plan["stream_id"] == stream_id:
            return plan
    raise HTTPException(status_code=404, detail=f"No supplier-loop plan found for stream ID {stream_id}.")


@router.get("/export/supplier-loop-plans.csv")
def export_supplier_loop_plans(db: Session = Depends(get_db)):
    """Export supplier-loop and circular procurement plans as CSV."""
    return _csv_response(_require_supplier_loop_plans(db), "circular-industry-ai-supplier-loop-plans.csv")
