# DebugIQ-backend/scripts/run_autonomous_workflow.py

from scripts import (
    autonomous_diagnose_issue,
    agent_suggest_patch,
    validate_proposed_patch,
    create_fix_pull_request,
    platform_data_api
)
import traceback # Import traceback to print full error details

def run_workflow_for_issue(issue_id: str):
    """
    Orchestrates the full autonomous bug resolution workflow.
    Steps: Fetch Issue -> Diagnosis -> Patch Suggestion -> Validate -> Create PR -> Update Status
    """
    print(f"🔁 Starting autonomous workflow for issue: {issue_id}")

    # Use platform_data_api to update status throughout the workflow
    platform_data_api.update_issue_status(issue_id, "Fetching Details")

    # 1. Fetch issue details and link repository info
    issue = platform_data_api.fetch_issue_details(issue_id)
    if not issue:
        platform_data_api.update_issue_status(issue_id, "Details Fetch Failed")
        print(f"❌ Workflow failed: Issue {issue_id} not found.")
        return {"error": "Issue not found", "issue_id": issue_id}

    repo_info = platform_data_api.get_repository_info_for_issue(issue_id)
    if not repo_info:
         platform_data_api.update_issue_status(issue_id, "Repository Not Linked")
         print(f"❌ Workflow failed: Repository not linked for issue {issue_id}.")
         return {"error": "Repository not linked", "issue_id": issue_id}


    platform_data_api.update_issue_status(issue_id, "Diagnosis in Progress")

    # 2. Run diagnosis
    try:
        diagnosis = autonomous_diagnose_issue.autonomous_diagnose(issue_id)
        if not diagnosis or diagnosis.get("root_cause") == "Could not determine root cause.":
            platform_data_api.update_issue_status(issue_id, "Diagnosis Failed")
            print(f"❌ Workflow failed: Diagnosis failed or was inconclusive for issue {issue_id}.")
            return {"error": "Diagnosis failed or inconclusive", "issue_id": issue_id, "diagnosis_result": diagnosis}

        platform_data_api.store_diagnosis_results(issue_id, diagnosis)
        platform_data_api.update_issue_status(issue_id, "Patch Suggestion in Progress")

    except Exception as e:
        platform_data_api.update_issue_status(issue_id, "Diagnosis Error")
        print(f"❌ Workflow error during diagnosis for issue {issue_id}: {e}")
        traceback.print_exc() # Print traceback for debugging
        return {"error": "Diagnosis error", "issue_id": issue_id, "details": str(e)}


    # 3. Suggest patch using AI agent
    try:
        patch_suggestion = agent_suggest_patch.agent_suggest_patch(issue_id, diagnosis)
        if not patch_suggestion or not patch_suggestion.get("suggested_patch_diff"):
             platform_data_api.update_issue_status(issue_id, "Patch Suggestion Failed")
             print(f"❌ Workflow failed: Patch suggestion failed or returned empty for issue {issue_id}.")
             return {"error": "Patch suggestion failed or empty", "issue_id": issue_id, "patch_suggestion_result": patch_suggestion}

        patch_diff = patch_suggestion["suggested_patch_diff"]
        platform_data_api.store_patch_suggestion(issue_id, patch_suggestion)
        platform_data_api.update_issue_status(issue_id, "Patch Validation in Progress")

    except Exception as e:
        platform_data_api.update_issue_status(issue_id, "Patch Suggestion Error")
        print(f"❌ Workflow error during patch suggestion for issue {issue_id}: {e}")
        traceback.print_exc() # Print traceback for debugging
        return {"error": "Patch suggestion error", "issue_id": issue_id, "details": str(e)}


    # 4. Validate patch
    try:
        validation = validate_proposed_patch.validate_patch(issue_id, patch_diff)
        platform_data_api.store_validation_results(issue_id, validation)

        if not validation.get("is_valid"):
            platform_data_api.update_issue_status(issue_id, "Patch Validation Failed")
            print(f"❌ Workflow failed: Patch validation failed for issue {issue_id}.")
            return {"error": "Patch validation failed", "validation": validation, "issue_id": issue_id}

        platform_data_api.update_issue_status(issue_id, "Patch Validated")

    except Exception as e:
        platform_data_api.update_issue_status(issue_id, "Patch Validation Error")
        print(f"❌ Workflow error during patch validation for issue {issue_id}: {e}")
        traceback.print_exc() # Print traceback for debugging
        return {"error": "Patch validation error", "issue_id": issue_id, "details": str(e)}

    # 5. Create PR
    try:
        # Construct a branch name based on the issue ID - make it safe for branch names
        safe_issue_id = issue_id.lower().replace(" ", "-").replace("_", "-")
        branch_name = f"debugiq/fix-{safe_issue_id}"

        pr = create_fix_pull_request.create_pull_request(
            issue_id=issue_id,
            branch_name=branch_name,
            code_diff=patch_diff,
            diagnosis_details=diagnosis,
            validation_results=validation
        )

        if "error" in pr:
            platform_data_api.update_issue_status(issue_id, "PR Creation Failed")
            print(f"❌ Workflow failed: PR creation failed for issue {issue_id}. Details: {pr['error']}")
            return {"error": "PR creation failed", "details": pr, "issue_id": issue_id}

        platform_data_api.store_pull_request_details(issue_id, pr)
        platform_data_api.update_issue_status(issue_id, "PR Created - Awaiting Review/QA")
        print(f"✅ Workflow completed for issue: {issue_id}. PR created: {pr.get('url')}")
        return {"message": "Workflow completed", "pull_request": pr, "issue_id": issue_id}

    except Exception as e:
        platform_data_api.update_issue_status(issue_id, "PR Creation Error")
        print(f"❌ Workflow error during PR creation for issue {issue_id}: {e}")
        traceback.print_exc() # Print traceback for debugging
        return {"error": "PR creation error", "issue_id": issue_id, "details": str(e)}


# Example usage (this would typically be triggered by an API endpoint)
if __name__ == "__main__":
    # This part demonstrates how the workflow could be run.
    # In your FastAPI app, an endpoint would call this function.
    # You'll need to configure the platform_data_api.db with a mock issue
    # that has a 'repository' URL pointing to a real or mock git repo for testing.

    print("--- Running Autonomous Workflow Simulation ---")
    # Setup a mock issue in the database for the workflow to process
    platform_data_api.db["ISSUE-SIM-TEST"] = {
        "id": "ISSUE-SIM-TEST",
        "title": "Simulated Bug for Workflow Test",
        "description": "This is a test issue to run the full autonomous workflow.",
        "status": "Open",
        "repository": "https://github.com/your-org/your-repo.git", # <-- **IMPORTANT:** Replace with a real repo URL for testing git operations
        "relevant_files": ["README.md"], # Files to fetch for context
        "logs": "Simulated log output indicating an error.",
        "error_message": "Simulated error: Something went wrong.",
        "assigned_to": "autonomous-agent",
        "diagnosis": None,
        "patch_suggestion": None,
        "validation_results": None,
        "pull_request": None
    }
    print("Mock issue 'ISSUE-SIM-TEST' added to mock DB.")
    print("\nNOTE: For this simulation to perform git operations, the 'repository' URL above must be a real repository accessible by the system running this script.")
    print("NOTE: You also need 'git' executable, and potentially configure credentials.")


    mock_issue_to_run = "ISSUE-SIM-TEST"
    print(f"\nSimulating running workflow for {mock_issue_to_run}...")
    result = run_workflow_for_issue(mock_issue_to_run)
    print("\n--- Workflow Simulation Result ---")
    import json
    print(json.dumps(result, indent=2))

    print("\n--- Mock DB state after workflow simulation ---")
    print(json.dumps(platform_data_api.db.get(mock_issue_to_run), indent=2))

    # Clean up the mock issue
    del platform_data_api.db["ISSUE-SIM-TEST"]
