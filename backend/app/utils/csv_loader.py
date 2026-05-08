"""Load industrial stream data from CSV into validated schemas."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from app import schemas
from app.utils.validation import normalise_hazardous_flag, validate_required_columns

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SAMPLE_CSV = PROJECT_ROOT / "data" / "sample_industrial_streams.csv"


def load_streams_from_csv(csv_path: Path = DEFAULT_SAMPLE_CSV) -> list[schemas.IndustrialStreamCreate]:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)
    validate_required_columns(df)

    records: list[schemas.IndustrialStreamCreate] = []
    for _, row in df.iterrows():
        records.append(
            schemas.IndustrialStreamCreate(
                stream_id=str(row["stream_id"]).strip(),
                stream_name=str(row["stream_name"]).strip(),
                material=str(row["material"]).strip(),
                source_process=str(row["source_process"]).strip(),
                monthly_quantity_kg=float(row["monthly_quantity_kg"]),
                current_route=str(row["current_route"]).strip(),
                disposal_cost_per_month=float(row["disposal_cost_per_month"]),
                contamination_risk=str(row["contamination_risk"]).strip().lower(),
                hazardous_flag=normalise_hazardous_flag(row["hazardous_flag"]),
                department=str(row["department"]).strip(),
                supplier=str(row["supplier"]).strip(),
                supplier_takeback_available=str(row["supplier_takeback_available"]).strip().lower(),
                recycled_content_available=str(row["recycled_content_available"]).strip().lower(),
                notes=str(row["notes"]).strip() if not pd.isna(row["notes"]) else None,
            )
        )
    return records
