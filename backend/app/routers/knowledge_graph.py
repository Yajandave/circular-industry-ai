"""Knowledge graph endpoints for relationship-based circular intelligence."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.knowledge_graph.service import build_knowledge_graph_catalog, build_stream_knowledge_graph

router = APIRouter(prefix="/api/knowledge/graph", tags=["knowledge graph"])


@router.get("", response_model=schemas.KnowledgeGraphResult)
def knowledge_graph_catalog() -> schemas.KnowledgeGraphResult:
    """Return a lightweight relationship graph for the controlled knowledge base."""
    return build_knowledge_graph_catalog()


@router.post("/match", response_model=schemas.KnowledgeGraphResult)
def match_stream_knowledge_graph(stream: schemas.KnowledgeStreamInput) -> schemas.KnowledgeGraphResult:
    """Build a stream-specific knowledge graph from raw stream-like input."""
    return build_stream_knowledge_graph(stream)


@router.get("/stream/{stream_id}", response_model=schemas.KnowledgeGraphResult)
def existing_stream_knowledge_graph(
    stream_id: str,
    db: Session = Depends(get_db),
) -> schemas.KnowledgeGraphResult:
    """Build a stream-specific knowledge graph for an existing loaded stream."""
    stream = crud.get_stream_by_stream_id(db, stream_id=stream_id)
    if stream is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Industrial stream not found: {stream_id}",
        )

    return build_stream_knowledge_graph(stream)
