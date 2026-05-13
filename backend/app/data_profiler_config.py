
"""Static configuration for the Data Profiler.

This module keeps role aliases, labels, value hints and workspace rules separate from profiler execution logic.
"""

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
