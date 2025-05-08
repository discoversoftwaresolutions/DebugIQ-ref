from pathlib import Path

# Production-ready autonomous workflow orchestration script
workflow_code = '''
import os
import sys
from .utils import platform_data_api
from .create_fix_pull_request import create_pull_request

def run_workflow_for_issue(issue_id):
    """
    Coordinates the autonomous workflow: diagnosis, patching, validation, PR creation.
    """
    print(f"[🚦] Orchestrating autonomous fix for Issue ID: {issue_id}")

    # Step 1: Verify inputs and readiness
    issue = platform_data_api.fetch_issue_details(issue_id)
    if not issue:
        print("[❌] Issue not found.")
        return False

    # Step 2: Fetch validation results and evaluate
    validation_results = platform_data_api.get_validation_results(issue_id)
    if not validation_results.get("is_valid", False):
        print("[🛑] Patch validation failed. Stopping workflow.")
        platform_data_api.update_issue_status(issue_id, "Validation Failed - Manual Review")
        return False
    platform_data_api.update_issue_status(issue_id, "Patch Validated - Ready for PR")

    # Step 3: Generate PR using AI
    diagnosis = platform_data_api.get_diagnosis(issue_id)
    patch = platform_data_api.get_proposed_patch(issue_id)
    pr_details = create_pull_request(
        issue_id=issue_id,
        branch_name=f"debugiq/fix-{issue_id.lower()}",
        code_diff=patch["suggested_patch_diff"],
        diagnosis_details=diagnosis,
        validation_results=validation_results
    )

    if not pr_details:
        print("[❌] PR creation failed.")
        platform_data_api.update_issue_status(issue_id, "PR Creation Failed - Needs Review")
        return False

    print(f"[✅] PR created: {pr_details.get('url')}")
    platform_data_api.update_issue_status(issue_id, "PR Created - Awaiting Review")

    # Step 4: Placeholder for QA evaluation trigger
    # Triggered externally after CI run and QA hooks complete
    return True
'''.strip()

workflow_path = Path("/mnt/data/DebugIQ-backend/scripts/run_autonomous_workflow.py")
workflow_path.parent.mkdir(parents=True, exist_ok=True)
workflow_path.write_text(workflow_code + "\n")

workflow_path
