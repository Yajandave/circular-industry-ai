"""API routes for industrial material and waste streams."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db, init_db
from app.utils.csv_loader import load_streams_from_csv, load_streams_from_upload_bytes

router = APIRouter(prefix="/api/streams", tags=["streams"])


@router.post("/load-sample", response_model=schemas.LoadSampleResponse)
def load_sample_streams(db: Session = Depends(get_db)) -> schemas.LoadSampleResponse:
    """Load the synthetic sample dataset into SQLite, replacing existing rows."""
    init_db()
    streams = load_streams_from_csv()
    loaded_rows = crud.bulk_replace_streams(db, streams)
    return schemas.LoadSampleResponse(
        loaded_rows=loaded_rows,
        replaced_existing_rows=True,
        message="Sample industrial stream dataset loaded into SQLite.",
    )


@router.post("/upload-csv", response_model=schemas.LoadSampleResponse)
async def upload_stream_csv(
    file: UploadFile = File(..., description="CSV file matching the Circular Industry AI data dictionary."),
    db: Session = Depends(get_db),
) -> schemas.LoadSampleResponse:
    """Upload a custom industrial stream CSV, validate it, and replace existing stream rows."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload must be a .csv file.",
        )

    try:
        file_bytes = await file.read()
        streams = load_streams_from_upload_bytes(file_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:  # pandas/parser errors should be shown as controlled bad requests
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not parse uploaded CSV: {exc}",
        ) from exc

    loaded_rows = crud.bulk_replace_streams(db, streams)
    return schemas.LoadSampleResponse(
        loaded_rows=loaded_rows,
        replaced_existing_rows=True,
        message=f"Uploaded CSV '{file.filename}' loaded into SQLite.",
    )


@router.get("", response_model=list[schemas.IndustrialStreamRead])
def list_streams(
    material: str | None = Query(default=None),
    department: str | None = Query(default=None),
    hazardous_flag: str | None = Query(default=None, description="Filter by true, false or unknown"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[schemas.IndustrialStreamRead]:
    """Return industrial streams, with basic filters for Milestone 2."""
    return crud.get_streams(
        db,
        material=material,
        department=department,
        hazardous_flag=hazardous_flag,
        skip=skip,
        limit=limit,
    )


@router.get("/summary", response_model=schemas.StreamSummary)
def stream_summary(db: Session = Depends(get_db)) -> schemas.StreamSummary:
    """Return basic portfolio-friendly summary metrics for the loaded dataset."""
    return crud.get_stream_summary(db)


@router.get("/{stream_id}", response_model=schemas.IndustrialStreamRead)
def get_stream(stream_id: str, db: Session = Depends(get_db)) -> schemas.IndustrialStreamRead:
    """Return one industrial stream by its business stream ID, such as S001."""
    stream = crud.get_stream_by_stream_id(db, stream_id=stream_id)
    if stream is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Industrial stream not found: {stream_id}",
        )
    return stream
