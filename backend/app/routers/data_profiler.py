"""Data profiler API endpoints for Milestone 14A."""

from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app import schemas
from app.data_profiler import profile_csv_bytes
from app.flexible_circular_import import build_flexible_circular_core_import
from app.mapping_validation import validate_confirmed_mapping

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

@router.post("/validate-mapping", response_model=schemas.ConfirmedMappingValidationReport)
def validate_mapping(
    payload: schemas.ConfirmedMappingValidationRequest,
) -> schemas.ConfirmedMappingValidationReport:
    """Validate user-confirmed mappings before future flexible import."""
    try:
        return validate_confirmed_mapping(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not validate confirmed mapping: {exc}",
        ) from exc

@router.post(
    "/build-circular-core-draft-import",
    response_model=schemas.FlexibleCircularCoreImportReport,
)
def build_circular_core_draft_import(
    payload: schemas.FlexibleCircularCoreImportRequest,
) -> schemas.FlexibleCircularCoreImportReport:
    """Build draft Circular Core rows from user-confirmed mapped source rows.

    This endpoint does not persist rows, run recommendations or verify impact.
    """
    try:
        return build_flexible_circular_core_import(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not build Circular Core draft import: {exc}",
        ) from exc
