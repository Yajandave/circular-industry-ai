"""Product workflow diagnostics and readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.evidence_register import build_evidence_register, build_evidence_summary
from app.procurement.supplier_loop_engine import build_supplier_loop_plans, build_supplier_loop_summary

router = APIRouter(prefix="/api/diagnostics", tags=["product workflow diagnostics"])


def _step(name: str, status: str, detail: str, required_next_action: str) -> dict[str, str]:
    return {
        "name": name,
        "status": status,
        "detail": detail,
        "required_next_action": required_next_action,
    }


@router.get("/workflow-readiness", response_model=schemas.ProductWorkflowReadiness)
def workflow_readiness(db: Session = Depends(get_db)) -> schemas.ProductWorkflowReadiness:
    """Return product-grade readiness for the current local workflow state.

    This endpoint is deterministic and does not call any LLM. It is intended for
    Alpha hardening, smoke testing and local demo checks.
    """
    streams = crud.get_streams(db, limit=500)
    recommendations = crud.get_recommendations(db, limit=500)

    steps: list[dict[str, str]] = []
    steps.append(
        _step(
            "Backend health",
            "ready",
            "FastAPI application is responding and database session is available.",
            "None.",
        )
    )

    if streams:
        steps.append(
            _step(
                "Dataset loaded",
                "ready",
                f"{len(streams)} material streams are loaded.",
                "Proceed to rules-engine recommendation run.",
            )
        )
    else:
        steps.append(
            _step(
                "Dataset loaded",
                "blocked",
                "No material streams are currently loaded.",
                "Load sample data or upload a valid CSV before running analysis.",
            )
        )

    if recommendations:
        steps.append(
            _step(
                "Rules engine run",
                "ready",
                f"{len(recommendations)} locked recommendations are available.",
                "Proceed to evidence, supplier-loop and report checks.",
            )
        )
    else:
        steps.append(
            _step(
                "Rules engine run",
                "blocked",
                "No recommendations are currently available.",
                "Run POST /api/recommendations/run after loading streams.",
            )
        )

    evidence_summary = None
    supplier_summary = None

    if streams and recommendations:
        evidence_records = build_evidence_register(streams, recommendations)
        evidence_summary = build_evidence_summary(evidence_records)
        steps.append(
            _step(
                "Evidence register",
                "ready" if evidence_records else "blocked",
                f"{len(evidence_records)} evidence records are available.",
                "Use evidence gaps and claim-readiness fields before reporting.",
            )
        )

        supplier_plans = build_supplier_loop_plans(streams, recommendations)
        supplier_summary = build_supplier_loop_summary(supplier_plans)
        steps.append(
            _step(
                "Supplier-loop intelligence",
                "ready" if supplier_plans else "blocked",
                f"{len(supplier_plans)} supplier-loop plans are available.",
                "Use supplier-loop outputs for evidence requests and procurement review.",
            )
        )

        steps.append(
            _step(
                "AI-assisted outputs",
                "ready",
                "AI copilot, evidence explainer, supplier email draft and circular action report endpoints can operate from locked outputs. Fallback mode is available when LLMs are disabled.",
                "Use outputs as advisory text only; locked rule/evidence fields remain authoritative.",
            )
        )
    else:
        steps.append(
            _step(
                "Evidence register",
                "blocked",
                "Evidence register requires loaded streams and generated recommendations.",
                "Load data and run recommendations first.",
            )
        )
        steps.append(
            _step(
                "Supplier-loop intelligence",
                "blocked",
                "Supplier-loop plans require loaded streams and generated recommendations.",
                "Load data and run recommendations first.",
            )
        )
        steps.append(
            _step(
                "AI-assisted outputs",
                "blocked",
                "AI-assisted outputs require locked recommendations and supporting evidence context.",
                "Load data and run recommendations first.",
            )
        )

    blocked_steps = [step for step in steps if step["status"] == "blocked"]
    warning_steps = [step for step in steps if step["status"] == "warning"]

    if blocked_steps:
        alpha_exit_status = "not ready: blocked workflow steps remain"
    elif warning_steps:
        alpha_exit_status = "partially ready: warnings require review"
    else:
        alpha_exit_status = "ready for local beta-candidate demo"

    return schemas.ProductWorkflowReadiness(
        product_stage="Alpha 9A workflow hardening",
        backend_status="ready",
        alpha_exit_status=alpha_exit_status,
        total_streams=len(streams),
        total_recommendations=len(recommendations),
        ready_for_full_demo=not blocked_steps,
        evidence_summary=evidence_summary,
        supplier_loop_summary=supplier_summary,
        steps=steps,
        governance_note=(
            "Workflow readiness is deterministic. It does not verify legal compliance, supplier capability, "
            "carbon savings, financial savings or completed operational impact. It confirms whether the current "
            "local product workflow has the required data and locked outputs for a controlled demo/use cycle."
        ),
    )
