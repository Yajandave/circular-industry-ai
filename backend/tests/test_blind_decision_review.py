from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _review_batch(*, declared_blind=True):
    return {
        "reviewer_name": "External Reviewer",
        "reviewer_role": "Waste and Resource Specialist",
        "reviewer_organisation": "Independent Review Practice",
        "reviewer_declared_blind": declared_blind,
        "labels": [
            {
                "case_id": "gc_damaged_lithium_battery",
                "strategy_category": "human review required",
                "risk_level": "high",
                "human_review_required": True,
                "confidence": 5,
                "reasoning": "Damaged battery condition requires specialist handling review before route selection.",
            },
            {
                "case_id": "gc_metal_trim_prevention",
                "strategy_category": "reduce / process redesign",
                "risk_level": "medium",
                "human_review_required": False,
                "confidence": 4,
                "reasoning": "Prevention should be prioritised, but I would initially retain medium screening risk.",
            },
        ],
    }


def test_blind_review_pack_withholds_system_answers_and_grounded_labels():
    response = client.get("/api/decision-validation/blind-review-pack")

    assert response.status_code == 200
    pack = response.json()
    assert len(pack) == 10

    hidden_keys = {
        "constraints",
        "interpretation",
        "sources",
        "source_ids",
        "label_source",
        "validation_status",
        "rule_applied",
        "recommended_circular_action",
        "circular_strategy_category",
        "risk_level",
        "human_review_required",
        "actual",
        "expected",
    }

    for case in pack:
        assert set(case).isdisjoint(hidden_keys)
        assert set(case) == {
            "case_id",
            "case_number",
            "jurisdiction",
            "stream",
            "reviewer_prompt",
            "blind_pack_note",
        }
        assert "Circular Industry AI" in case["blind_pack_note"]
        assert "system" not in case["stream"]

    assert pack[0]["case_number"] == 1
    assert pack[-1]["case_number"] == 10


def test_blind_review_submission_persists_system_snapshot_and_separate_agreement_metrics():
    response = client.post(
        "/api/decision-validation/blind-review-submit",
        json=_review_batch(),
    )

    assert response.status_code == 200
    result = response.json()

    assert result["reviewer_declared_blind"] is True
    assert result["total_labels"] == 2
    assert result["strategy_agreement_count"] == 2
    assert result["strategy_agreement_pct"] == 100.0
    assert result["risk_agreement_count"] == 1
    assert result["risk_agreement_pct"] == 50.0
    assert result["human_review_agreement_count"] == 2
    assert result["human_review_agreement_pct"] == 100.0
    assert result["full_agreement_count"] == 1
    assert result["full_agreement_pct"] == 50.0
    assert result["submission_batch_id"].startswith("blind-review-")
    assert "coarse measure" in result["governance_note"].lower()
    assert "does not by itself prove reviewer independence" in result["governance_note"].lower()

    battery = next(
        item
        for item in result["submissions"]
        if item["case_id"] == "gc_damaged_lithium_battery"
    )
    assert battery["system_rule_applied"] == "R001_HAZARDOUS_OR_UNKNOWN_REVIEW"
    assert battery["system_strategy_category"] == "human review required"
    assert battery["system_risk_level"] == "high"
    assert battery["system_human_review_required"] is True
    assert battery["strategy_agreement"] is True
    assert battery["risk_agreement"] is True
    assert battery["human_review_agreement"] is True

    trim = next(
        item
        for item in result["submissions"]
        if item["case_id"] == "gc_metal_trim_prevention"
    )
    assert trim["system_strategy_category"] == "reduce / process redesign"
    assert trim["system_risk_level"] == "low"
    assert trim["strategy_agreement"] is True
    assert trim["risk_agreement"] is False
    assert trim["human_review_agreement"] is True


def test_blind_review_history_returns_immutable_submissions():
    submit_response = client.post(
        "/api/decision-validation/blind-review-submit",
        json=_review_batch(),
    )
    assert submit_response.status_code == 200
    submitted = submit_response.json()

    history_response = client.get(
        "/api/decision-validation/blind-review-history?limit=100"
    )
    assert history_response.status_code == 200
    history = history_response.json()

    matching = [
        item
        for item in history["submissions"]
        if item["submission_batch_id"] == submitted["submission_batch_id"]
    ]
    assert len(matching) == 2
    assert history["unique_cases_reviewed"] >= 2
    assert history["unique_reviewers"] >= 1
    assert "should not be described as independent expert validation" in history["governance_note"].lower()


def test_blind_review_submission_creates_audit_event():
    response = client.post(
        "/api/decision-validation/blind-review-submit",
        json=_review_batch(),
    )
    assert response.status_code == 200
    batch = response.json()

    audit_response = client.get(
        "/api/audit/events?event_type=blind_decision_review_submitted&limit=50"
    )
    assert audit_response.status_code == 200
    event = next(
        item
        for item in audit_response.json()
        if item["entity_id"] == batch["submission_batch_id"]
    )
    assert event["metadata_json"]["reviewer_declared_blind"] is True
    assert event["metadata_json"]["total_labels"] == 2
    assert event["metadata_json"]["strategy_agreement_pct"] == 100.0
    assert event["metadata_json"]["risk_agreement_pct"] == 50.0
    assert "does not establish independent expert validation" in event["claim_boundary"].lower()


def test_blind_review_submission_rejects_nonblind_reviewer():
    response = client.post(
        "/api/decision-validation/blind-review-submit",
        json=_review_batch(declared_blind=False),
    )

    assert response.status_code == 400
    assert "declare" in response.json()["detail"].lower()


def test_blind_review_submission_rejects_duplicate_case_labels():
    payload = _review_batch()
    payload["labels"].append(dict(payload["labels"][0]))

    response = client.post(
        "/api/decision-validation/blind-review-submit",
        json=payload,
    )

    assert response.status_code == 400
    assert "one label per case" in response.json()["detail"].lower()


def test_blind_review_submission_rejects_unknown_case():
    payload = _review_batch()
    payload["labels"][0]["case_id"] = "gc_not_a_real_case"

    response = client.post(
        "/api/decision-validation/blind-review-submit",
        json=payload,
    )

    assert response.status_code == 400
    assert "unknown blind-review case ids" in response.json()["detail"].lower()


def test_blind_review_submission_rejects_blank_reviewer_identity():
    payload = _review_batch()
    payload["reviewer_name"] = "   "

    response = client.post(
        "/api/decision-validation/blind-review-submit",
        json=payload,
    )

    assert response.status_code == 400
    assert "reviewer name" in response.json()["detail"].lower()
