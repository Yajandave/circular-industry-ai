"""Knowledge retrieval endpoints for stream-level intelligence."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.knowledge_base.loader import validate_knowledge_base
from app.knowledge_base.retriever import retrieve_knowledge_for_stream

router = APIRouter(prefix="/api/knowledge", tags=["knowledge retrieval"])


@router.get("/validate", response_model=schemas.KnowledgeValidationSummary)
def validate_knowledge() -> schemas.KnowledgeValidationSummary:
    """Validate the structured knowledge base."""
    return validate_knowledge_base()


@router.post("/match", response_model=schemas.KnowledgeRetrievalResult)
def match_stream_knowledge(
    stream: schemas.KnowledgeStreamInput,
    include_full_records: bool = Query(default=False),
) -> schemas.KnowledgeRetrievalResult:
    """Retrieve relevant knowledge for a stream-like input payload."""
    return retrieve_knowledge_for_stream(stream, include_full_records=include_full_records)


@router.get("/stream/{stream_id}", response_model=schemas.KnowledgeRetrievalResult)
def match_existing_stream_knowledge(
    stream_id: str,
    include_full_records: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> schemas.KnowledgeRetrievalResult:
    """Retrieve relevant knowledge for an existing loaded stream."""
    stream = crud.get_stream_by_stream_id(db, stream_id=stream_id)
    if stream is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Industrial stream not found: {stream_id}",
        )

    return retrieve_knowledge_for_stream(stream, include_full_records=include_full_records)
