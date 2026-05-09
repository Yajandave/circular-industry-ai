"""Site-wide AI copilot endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.ai_copilot.service import generate_site_copilot_summary
from app.database import get_db

router = APIRouter(prefix="/api/ai-copilot", tags=["site-wide AI copilot"])


@router.get("/site-summary", response_model=schemas.SiteAICopilotSummary)
def get_site_copilot_summary(db: Session = Depends(get_db)) -> schemas.SiteAICopilotSummary:
    """Generate a site-wide advisory AI copilot summary from locked outputs."""
    streams = crud.get_streams(db, limit=500)
    recommendations = crud.get_recommendations(db, limit=500)

    if not streams:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No industrial streams found. Run POST /api/streams/load-sample first.",
        )

    if not recommendations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No recommendations found. Run POST /api/recommendations/run first.",
        )

    return generate_site_copilot_summary(streams, recommendations)
