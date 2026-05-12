"""Milestone 14A backend data profiler and column alias mapper."""

from __future__ import annotations

from io import BytesIO
import re

import pandas as pd

GOVERNANCE_NOTE = (
    "This profiler maps uploaded CSV structure into possible workspace routes. "
    "It does not invent missing data, verify savings, verify diversion, verify environmental impact, "
    "confirm supplier compliance, approve claims, determine legal compliance or determine statutory EIA significance."
)

ROLE_ALIASES = {
    "stream_id": ["stream_id", "stream id", "id", "record id", "waste id", "material id", "stream reference"],
    "stream_name": ["stream_name", "stream name", "waste stream", "material stream", "item", "description", "waste description"],
    "material": ["material", "material type", "waste material", "base material", "substance", "resource type", "material category"],
    "waste_stream_type": ["waste type", "waste category", "stream type", "waste classification", "waste stream type", "condition"],
    "source_process": ["source_process", "source process", "process", "origin", "activity", "production line"],
    "quantity": ["monthly_quantity_kg", "quantity", "qty", "weight", "waste weight", "monthly weight", "monthly quantity", "tonnage", "volume generated", "amount generated"],
    "quantity_unit": ["unit", "units", "uom", "quantity unit", "weight unit"],
    "current_route": ["current_route", "current route", "route", "disposal route", "waste route", "treatment route", "destination", "handling method", "recovery route", "disposal method"],
    "disposal_cost_per_month": ["disposal_cost_per_month", "disposal cost", "monthly disposal cost", "waste cost", "handling cost", "monthly cost", "disposal charge", "cost per month"],
    "contamination_risk": ["contamination_risk", "contamination risk", "contamination", "contamination level", "cleanliness"],
    "hazardous_flag": ["hazardous_flag", "hazardous", "hazardous status", "hazard flag", "dangerous", "hazardous waste", "hazard"],
    "department": ["department", "site area", "business unit", "function", "team", "location", "area"],
    "supplier": ["supplier", "supplier name", "vendor", "vendor name", "contractor", "provider", "waste contractor"],
    "supplier_takeback_available": ["supplier_takeback_available", "takeback", "take back", "supplier takeback", "return scheme", "returnable", "reverse logistics"],
    "recycled_content_available": ["recycled_content_available", "recycled content", "secondary material", "recycled input"],
    "notes": ["notes", "comments", "remarks", "observations", "additional information"],
    "reporting_year": ["year", "reporting year", "period", "date", "fiscal year", "financial year"],
    "esg_score": ["esg score", "score", "sustainability score", "rating score"],
    "esg_rating": ["rating", "esg rating", "provider rating", "grade"],
    "esg_theme": ["theme", "pillar", "esg theme", "topic", "indicator"],
    "evidence": ["evidence", "documentation", "proof", "source", "substantiation", "supporting evidence"],
    "emission_scope": ["scope", "ghg scope", "emissions scope", "scope category"],
    "emissions_quantity": ["emissions", "tco2e", "co2e", "carbon emissions", "emission amount", "kgco2e", "tonnes co2e"],
    "emission_source": ["emission source", "source", "fuel", "activity", "category", "emissions category"],
    "emission_factor": ["emission factor", "ef", "conversion factor", "carbon factor"],
    "baseline_year": ["baseline year", "base year"],
    "target_year": ["target year", "net zero target year", "reduction target year"],
    "eia_topic": ["eia topic", "environmental topic", "topic", "discipline", "assessment topic"],
    "receptor": ["receptor", "sensitive receptor", "environmental receptor", "receiver"],
    "impact": ["impact", "effect", "environmental effect", "potential impact"],
    "magnitude": ["magnitude", "impact magnitude"],
    "sensitivity": ["sensitivity", "receptor sensitivity"],
    "significance": ["significance", "effect significance", "residual significance"],
    "mitigation": ["mitigation", "mitigation measure", "control measure", "commitment"],
    "residual_effect": ["residual effect", "residual impact"],
    "monitoring": ["monitoring", "monitoring requirement", "follow up"],
    "stakeholder": ["stakeholder", "consultee", "respondent", "authority"],
    "claim_text": ["claim", "claim text", "sustainability claim", "marketing claim", "statement"],
    "claim_type": ["claim type", "type", "claim category"],
    "product": ["product", "sku", "product name", "item name"],
    "certificate": ["certificate", "certification", "standard certificate"],
    "standard": ["standard", "framework", "scheme", "protocol"],
    "verification_status": ["verification status", "verified", "verification", "assurance status", "validated"],
    "geography": ["geography", "country", "market", "region"],
    "spend": ["spend", "annual spend", "monthly spend", "purchase value", "procurement spend", "cost"],
    "procurement_category": ["category", "procurement category", "supplier category", "commodity", "purchase category"],
    "supplier_country": ["supplier country", "country", "supplier location", "origin country"],
    "contract_status": ["contract status", "contract", "agreement status"],
}

ROLE_LABELS = {role: role.replace("_", " ").title() for role in ROLE_ALIASES}
ROLE_LABELS.update({
    "current_route": "Current route",
    "disposal_cost_per_month": "Disposal cost per month",
    "hazardous_flag": "Hazardous status",
    "waste_stream_type": "Waste / stream type",
    "claim_text": "Claim text",
    "emissions_quantity": "Emissions quantity",
    "emission_scope": "GHG scope",
    "eia_topic": "EIA topic",
})

VALUE_HINTS = {
    "material": ["steel", "metal", "plastic", "cardboard", "wood", "solvent", "glass", "rubber", "textile", "paper", "aluminium", "copper"],
    "waste_stream_type": ["scrap", "offcut", "packaging", "spent", "residue", "pallet", "waste", "contaminated", "mixed"],
    "current_route": ["recycling", "recycle", "landfill", "disposal", "reuse", "recovery", "incineration", "takeback", "return", "treatment"],
    "contamination_risk": ["low", "medium", "high", "unknown", "clean", "contaminated"],
    "hazardous_flag": ["true", "false", "yes", "no", "hazardous", "non hazardous", "unknown"],
    "emission_scope": ["scope 1", "scope 2", "scope 3"],
    "claim_text": ["carbon neutral", "net zero", "recyclable", "biodegradable", "compostable", "plastic free", "zero waste"],
    "claim_type": ["carbon neutral", "net zero", "recyclable", "biodegradable", "compostable", "plastic free", "zero waste"],
    "eia_topic": ["air quality", "noise", "biodiversity", "water", "transport", "climate", "heritage", "landscape", "waste"],
}

WORKSPACE_RULES = {
    "circular-core": {
        "label": "Circular Core",
        "required": ["material", "quantity", "current_route"],
        "important": ["stream_name", "source_process", "disposal_cost_per_month", "contamination_risk", "hazardous_flag", "supplier"],
        "available": ["material-flow screening with mapped columns", "screened quantity and route review", "supplier evidence request routing where supplier data exists", "cost exposure screening where cost data exists"],
        "unavailable": ["verified diversion or verified savings", "hazardous and contamination-sensitive review if those fields are missing", "legal compliance or waste classification approval"],
    },
    "esg": {
        "label": "ESG",
        "required": ["esg_score", "reporting_year"],
        "important": ["esg_rating", "esg_theme", "evidence"],
        "available": ["ESG score trend screening", "rating/evidence gap review", "internal briefing summary"],
        "unavailable": ["verified ESG performance", "external rating validation"],
    },
    "ghg-net-zero": {
        "label": "GHG & Net Zero",
        "required": ["emissions_quantity"],
        "important": ["emission_scope", "emission_source", "baseline_year", "target_year", "emission_factor"],
        "available": ["emissions source profile", "scope/category screening", "data gap review"],
        "unavailable": ["verified emissions inventory", "carbon neutrality or net zero achievement confirmation"],
    },
    "eia": {
        "label": "EIA",
        "required": ["eia_topic", "impact"],
        "important": ["receptor", "magnitude", "sensitivity", "significance", "mitigation", "residual_effect", "stakeholder"],
        "available": ["issue register screening", "topic/receptor/impact mapping", "mitigation and evidence gap review"],
        "unavailable": ["statutory EIA significance determination", "planning acceptability or legal compliance decision"],
    },
    "greenwashing-claims": {
        "label": "Greenwashing / Claims",
        "required": ["claim_text"],
        "important": ["claim_type", "product", "evidence", "certificate", "standard", "verification_status", "geography"],
        "available": ["claim type classification", "evidence sufficiency screen", "missing evidence request list"],
        "unavailable": ["legal claim approval", "third-party verification or certification"],
    },
    "supplier-procurement": {
        "label": "Supplier & Procurement",
        "required": ["supplier"],
        "important": ["spend", "procurement_category", "supplier_country", "certificate", "contract_status", "supplier_takeback_available"],
        "available": ["supplier data gap profile", "spend/category exposure screening", "supplier evidence request routing"],
        "unavailable": ["verified supplier compliance", "contract/legal approval"],
    },
    "data-profiler": {
        "label": "Data Profiler",
        "required": [],
        "important": [],
        "available": ["column profiling", "alias mapping", "workspace routing", "missing field review"],
        "unavailable": ["domain analysis without mapped and confirmed data roles"],
    },
}


def _normalise(value: object) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[_\-/]+", " ", text)
    text = re.sub(r"[^a-z0-9£% ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _tokens(value: object) -> set[str]:
    return {token for token in _normalise(value).split(" ") if token}


def _samples(series: pd.Series, limit: int = 6) -> list[str]:
    values = []
    for value in series.dropna().astype(str).head(40).tolist():
        cleaned = value.strip()
        if cleaned and cleaned.lower() not in {"nan", "none", "null"} and cleaned not in values:
            values.append(cleaned)
        if len(values) >= limit:
            break
    return values


def _infer_type(series: pd.Series) -> str:
    non_null = series.dropna()
    if non_null.empty:
        return "empty"
    numeric = pd.to_numeric(non_null, errors="coerce")
    if numeric.notna().mean() >= 0.85:
        return "numeric"
    dates = pd.to_datetime(non_null, errors="coerce")
    if dates.notna().mean() >= 0.75:
        return "date"
    unique_ratio = non_null.astype(str).nunique(dropna=True) / max(len(non_null), 1)
    return "categorical" if unique_ratio <= 0.35 else "text"


def _value_score(role: str, samples: list[str]) -> int:
    joined = " ".join(samples).lower()
    return min(18, sum(1 for hint in VALUE_HINTS.get(role, []) if hint in joined) * 6)


def _type_score(role: str, inferred_type: str, header: str) -> int:
    numeric_roles = {"quantity", "disposal_cost_per_month", "spend", "emissions_quantity", "emission_factor", "esg_score"}
    year_roles = {"reporting_year", "baseline_year", "target_year"}
    if role in numeric_roles and inferred_type == "numeric":
        return 10
    if role in year_roles and inferred_type in {"date", "numeric"}:
        return 8
    if role == "disposal_cost_per_month" and ("£" in header or "cost" in header or "spend" in header):
        return 8
    return 0


def _role_candidates(header: str, series: pd.Series) -> list[dict]:
    normalised = _normalise(header)
    header_tokens = _tokens(header)
    samples = _samples(series)
    inferred_type = _infer_type(series)
    candidates = []

    for role, aliases in ROLE_ALIASES.items():
        best_score = 0
        best_reason = ""
        for alias in aliases:
            alias_norm = _normalise(alias)
            alias_tokens = _tokens(alias)
            if normalised == alias_norm:
                score = 86
                reason = f"header matches alias '{alias}'"
            elif alias_norm and alias_norm in normalised:
                score = 74
                reason = f"header contains alias '{alias}'"
            else:
                score = int((len(header_tokens & alias_tokens) / max(len(alias_tokens), 1)) * 58)
                reason = f"header token overlap with alias '{alias}'"
            score += _value_score(role, samples)
            score += _type_score(role, inferred_type, normalised)
            if score > best_score:
                best_score = score
                best_reason = reason
        if best_score >= 35:
            candidates.append({"role": role, "label": ROLE_LABELS.get(role, role), "confidence": min(best_score, 99), "reason": best_reason})

    return sorted(candidates, key=lambda item: item["confidence"], reverse=True)[:4]


def _column_profile(name: str, series: pd.Series) -> dict:
    candidates = _role_candidates(name, series)
    top = candidates[0] if candidates else None
    second = candidates[1] if len(candidates) > 1 else None
    gap = (top["confidence"] - second["confidence"]) if top and second else 100
    missing = int(series.isna().sum())
    total = len(series)

    return {
        "original_name": str(name),
        "normalised_name": _normalise(name),
        "inferred_data_type": _infer_type(series),
        "missing_count": missing,
        "missing_percentage": round((missing / total) * 100, 2) if total else 0.0,
        "unique_count": int(series.nunique(dropna=True)),
        "sample_values": _samples(series),
        "mapped_role": top["role"] if top else None,
        "mapped_role_label": top["label"] if top else None,
        "role_confidence": top["confidence"] if top else 0,
        "role_reason": top["reason"] if top else "No confident alias or value-pattern match.",
        "confirmation_required": bool(top and (top["confidence"] < 85 or gap < 12)),
        "alternatives": candidates[1:],
    }


def _role_mapping(columns: list[dict]) -> dict[str, dict]:
    mapping = {}
    for column in sorted(columns, key=lambda item: item["role_confidence"], reverse=True):
        role = column.get("mapped_role")
        if role and role not in mapping:
            mapping[role] = column
    return mapping


def _workspace_score(rule: dict, mapped_roles: set[str]) -> int:
    required = rule.get("required", [])
    important = rule.get("important", [])
    if not required:
        return 20
    required_hits = sum(1 for role in required if role in mapped_roles)
    important_hits = sum(1 for role in important if role in mapped_roles)
    return int(round((required_hits / len(required)) * 70 + (important_hits / max(len(important), 1)) * 30))


def _status(score: int) -> str:
    if score >= 80:
        return "strong match"
    if score >= 55:
        return "partial match"
    if score >= 30:
        return "weak match"
    return "not enough mapped data"


def _workspace_rows(mapped_roles: set[str]) -> list[dict]:
    rows = []
    for workspace_id, rule in WORKSPACE_RULES.items():
        score = 100 if workspace_id == "data-profiler" else _workspace_score(rule, mapped_roles)
        roles = rule.get("required", []) + rule.get("important", [])
        rows.append({
            "workspace_id": workspace_id,
            "label": rule["label"],
            "score": score,
            "status": "available profiler route" if workspace_id == "data-profiler" else _status(score),
            "matched_roles": [{"role": role, "label": ROLE_LABELS.get(role, role)} for role in roles if role in mapped_roles],
            "missing_roles": [{"role": role, "label": ROLE_LABELS.get(role, role)} for role in roles if role not in mapped_roles],
            "available_analysis": rule["available"],
            "unavailable_analysis": rule["unavailable"],
            "governance_boundary": GOVERNANCE_NOTE,
        })
    return sorted(rows, key=lambda row: row["score"], reverse=True)


def _summary(best: dict, mapped_roles: set[str]) -> tuple[list[str], list[str], str]:
    available = list(best["available_analysis"])
    unavailable = list(best["unavailable_analysis"])
    if "quantity" not in mapped_roles:
        unavailable.append("quantity-based screening until a quantity/weight column is mapped")
    if best["workspace_id"] == "circular-core":
        if "hazardous_flag" not in mapped_roles:
            unavailable.append("hazardous review is limited until hazardous status is provided")
        if "contamination_risk" not in mapped_roles:
            unavailable.append("contamination-sensitive recommendations are limited until contamination risk is provided")
        if "disposal_cost_per_month" not in mapped_roles:
            unavailable.append("cost exposure screening is unavailable until cost data is mapped")
    return available, unavailable, "Review the mapped columns and confirm uncertain roles before flexible import or domain analysis."


def profile_csv_bytes(file_bytes: bytes, dataset_label: str = "uploaded dataset") -> dict:
    if not file_bytes:
        raise ValueError("Uploaded CSV file is empty.")
    try:
        df = pd.read_csv(BytesIO(file_bytes), encoding="utf-8-sig")
    except Exception as exc:
        raise ValueError(f"Could not parse uploaded CSV: {exc}") from exc
    if len(df.columns) == 0:
        raise ValueError("Uploaded CSV does not contain columns.")

    columns = [_column_profile(column, df[column]) for column in df.columns]
    mapping = _role_mapping(columns)
    mapped_roles = set(mapping)
    workspace_rows = _workspace_rows(mapped_roles)
    non_profiler = [row for row in workspace_rows if row["workspace_id"] != "data-profiler"]
    best = next((row for row in non_profiler if row["score"] >= 30), workspace_rows[0])
    available, unavailable, next_action = _summary(best, mapped_roles)

    return {
        "dataset_label": dataset_label,
        "total_rows": int(len(df)),
        "total_columns": int(len(df.columns)),
        "duplicate_rows": int(df.duplicated().sum()),
        "detected_workspace": best["workspace_id"],
        "detected_workspace_label": best["label"],
        "workspace_confidence": int(best["score"]),
        "workspace_status": best["status"],
        "columns": columns,
        "role_mapping": [
            {
                "role": role,
                "label": ROLE_LABELS.get(role, role),
                "source_column": column["original_name"],
                "confidence": column["role_confidence"],
                "confirmation_required": column["confirmation_required"],
            }
            for role, column in mapping.items()
        ],
        "workspace_compatibility": workspace_rows,
        "available_analysis_routes": available,
        "unavailable_analysis_routes": unavailable,
        "recommended_next_action": next_action,
        "governance_note": GOVERNANCE_NOTE,
    }
