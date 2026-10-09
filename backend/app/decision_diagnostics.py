"""Safe read-only summaries of the existing deterministic decision validation suites.

Never include industrial data, full inputs, free-text reasoning or source material
in diagnostics exports. These suites use fixed in-memory cases, not the live DB.
"""

def collect_decision_validation():
    from app.decision_validation import run_decision_validation
    from app.grounded_decision_validation import run_grounded_challenge_validation

    results = []
    definitions = (
        ("internal_reference", run_decision_validation, "total_cases", "full_agreement_cases",
         "Internal reference expectations; not independent expert validation."),
        ("guidance_based_challenges", run_grounded_challenge_validation, "total_cases", "passing_cases",
         "Authoritative-guidance interpretation; not legal advice or independent assurance."),
    )
    for name, run, count_key, pass_key, caveat in definitions:
        try:
            data = run()
            total = int(data[count_key])
            passed = int(data[pass_key])
            failures = [
                {"case_id": str(r.get("case_id", "unknown")), "status": str(r.get("status", "unknown"))}
                for r in data.get("results", [])
                if r.get("status") not in ("pass",)
            ]
            # Fail closed if the expected suite is empty or incomplete.
            valid = total > 0 and 0 <= passed <= total
            status = "PASS" if valid and passed == total and not failures else "FAIL"
            results.append({
                "name": name,
                "status": status,
                "total_cases": total,
                "passed_cases": passed,
                "failed_cases": max(total - passed, len(failures)),
                "failed_case_ids": [f["case_id"] for f in failures],
                "methodology": caveat,
            })
        except Exception as exc:
            results.append({"name": name, "status": "FAIL", "error_type": type(exc).__name__, "methodology": caveat})
    return results
