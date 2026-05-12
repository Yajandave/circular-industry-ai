"""Data profiler API endpoints for Milestone 14A."""

from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app import schemas
from app.data_profiler import profile_csv_bytes

router = APIRouter(prefix="/api/data-profiler", tags=["data profiler"])


@router.post("/profile-csv", response_model=schemas.DataProfilerReport)
async def profile_csv(
    file: UploadFile = File(..., description="CSV file to profile without saving or strict-template loading."),
) -> schemas.DataProfilerReport:
    """Profile an uploaded CSV and recommend a workspace route without loading it."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload must be a .csv file.",
        )

    try:
        file_bytes = await file.read()
        return profile_csv_bytes(file_bytes, dataset_label=file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not profile uploaded CSV: {exc}",
        ) from exc
