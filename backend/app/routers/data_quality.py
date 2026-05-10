"""Data quality and import validation endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.data_quality import build_data_quality_report
from app.database import get_db
from app.utils.csv_loader import load_streams_from_upload_bytes

router = APIRouter(prefix="/api/data-quality", tags=["data quality"])


@router.get("/current", response_model=schemas.DataQualityReport)
def current_data_quality(db: Session = Depends(get_db)) -> schemas.DataQualityReport:
    """Return a data-quality report for the currently loaded stream dataset."""
    streams = crud.get_streams(db, limit=500)
    return build_data_quality_report(streams, dataset_label="current loaded dataset")


@router.post("/validate-csv", response_model=schemas.DataQualityReport)
async def validate_csv_without_loading(
    file: UploadFile = File(..., description="CSV file to validate without replacing current data."),
) -> schemas.DataQualityReport:
    """Validate an uploaded CSV and return a data-quality report without saving it."""
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
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not parse uploaded CSV: {exc}",
        ) from exc

    return build_data_quality_report(streams, dataset_label=file.filename)
