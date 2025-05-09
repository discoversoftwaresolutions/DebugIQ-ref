# Generate a clean, production-grade run_autonomous_workflow.py
workflow_code = '''
# scripts/run_autonomous_workflow.py

from scripts import (
    autonomous_diagnose_issue,
    validate_proposed_patch,
    create_fix_pull_request,
    platform_data_api
)

def run_workflow_for_issue(issue_id):
    """
    Orchestrates the full autonomous bug resolution workflow.
    Steps: Diagnosis → Patch Suggestion (mock) → Validate → Create PR
    """
    print(f"🔁 Starting autonomous workflow for issue: {issue_id}")

    # 1. Fetch and verify issue
    issue = platform_data_api.fetch_issue_details(issue_id)
    if not issue:
        return {"error": "Issue not found", "issue_id": issue_id}

    # 2. Run diagnosis
    diagnosis = autonomous_diagnose_issue.autonomous_diagnose(issue_id)
    if not diagnosis:
        platform_data_api.update_issue_status(issue_id, "Diagnosis Failed")
        return {"error": "Diagnosis failed", "issue_id": issue_id}

    # 3. Simulate patch suggestion (placeholder)
    patch_diff = f"- buggy_code()\n+ fixed_code()"  # You can wire agent_suggest_patch next
    patch_suggestion = {
        "suggested_patch_diff": patch_diff,
        "explanation": "Mock patch to demonstrate flow"
    }
    platform_data_api.update_issue_status(issue_id, "Patch Suggested")
    platform_data_api.db[issue_id]["patch_suggestion"] = patch_suggestion

    # 4. Validate patch
    validation = validate_proposed_patch.validate_patch(issue_id, patch_diff)
    platform_data_api.store_validation_results(issue_id, validation)
    if not validation["is_valid"]:
        platform_data_api.update_issue_status(issue_id, "Patch Validation Failed")
        return {"error": "Patch validation failed", "validation": validation}

    platform_data_api.update_issue_status(issue_id, "Patch Validated")

    # 5. Create PR
    pr = create_fix_pull_request.create_pull_request(
        issue_id=issue_id,
        branch_name=f"debugiq/fix-{issue_id.lower()}",
        code_diff=patch_diff,
        diagnosis_details=diagnosis,
        validation_results=validation
    )

    if "error" in pr:
        platform_data_api.update_issue_status(issue_id, "PR Creation Failed")
        return {"error": "PR creation failed", "details": pr}

    platform_data_api.update_issue_status(issue_id, "PR Created - Awaiting Review/QA")
    return {"message": "Workflow completed", "pull_request": pr}
'''.strip()

workflow_path.write_text(workflow_code + "\n")
