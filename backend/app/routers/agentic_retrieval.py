"""Agentic retrieval workflow endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.agentic_retrieval.service import run_agentic_retrieval_workflow
from app.database import get_db

router = APIRouter(prefix="/api/agentic-retrieval", tags=["agentic retrieval"])


@router.post("/run", response_model=schemas.AgenticRetrievalWorkflowResult)
def run_agentic_retrieval(
    stream: schemas.KnowledgeStreamInput,
) -> schemas.AgenticRetrievalWorkflowResult:
    """Run deterministic agentic retrieval for raw stream input without saving insight."""
    return run_agentic_retrieval_workflow(stream, save_insight=False)


@router.post("/run-and-save", response_model=schemas.AgenticRetrievalWorkflowResult)
def run_and_save_agentic_retrieval(
    stream: schemas.KnowledgeStreamInput,
    db: Session = Depends(get_db),
) -> schemas.AgenticRetrievalWorkflowResult:
    """Run deterministic agentic retrieval for raw stream input and save generated insight."""
    return run_agentic_retrieval_workflow(stream, db=db, save_insight=True)


@router.get("/stream/{stream_id}", response_model=schemas.AgenticRetrievalWorkflowResult)
def run_agentic_retrieval_for_existing_stream(
    stream_id: str,
    db: Session = Depends(get_db),
) -> schemas.AgenticRetrievalWorkflowResult:
    """Run deterministic agentic retrieval for an existing loaded stream without saving insight."""
    stream = crud.get_stream_by_stream_id(db, stream_id=stream_id)
    if stream is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Industrial stream not found: {stream_id}",
        )

    return run_agentic_retrieval_workflow(stream, save_insight=False)


@router.post("/stream/{stream_id}/run-and-save", response_model=schemas.AgenticRetrievalWorkflowResult)
def run_and_save_agentic_retrieval_for_existing_stream(
    stream_id: str,
    db: Session = Depends(get_db),
) -> schemas.AgenticRetrievalWorkflowResult:
    """Run deterministic agentic retrieval for an existing loaded stream and save generated insight."""
    stream = crud.get_stream_by_stream_id(db, stream_id=stream_id)
    if stream is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Industrial stream not found: {stream_id}",
        )

    return run_agentic_retrieval_workflow(stream, db=db, save_insight=True)
