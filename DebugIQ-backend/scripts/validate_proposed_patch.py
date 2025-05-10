# DebugIQ-backend/scripts/validate_proposed_patch.py

import os
import subprocess # To run system commands like git, test runners, linters
from scripts import platform_data_api
# Assuming you have configurations for test commands, linter commands, etc.
# from app.core.config import settings # Example import

# --- Configuration Placeholder ---
# In a real app, load commands for running tests, linters, etc.
# Example: settings.TEST_COMMAND, settings.LINT_COMMAND
TEST_COMMAND = ["pytest"] # Example command, replace with actual
LINT_COMMAND = ["flake8"] # Example command, replace with actual
STATIC_ANALYSIS_COMMAND = ["pylint"] # Example command, replace with actual
# --- End Configuration Placeholder ---


def run_command_in_repo(command: list[str], repo_path: str) -> tuple[int, str, str]:
    """Runs a command within the specified repository path."""
    print(f"Executing command in {repo_path}: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False # Don't raise exception on non-zero exit code
        )
        print(f"Command finished with exit code {result.returncode}")
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        print(f"Error: Command not found - {' '.join(command)}")
        return -1, "", f"Command not found: {command[0]}"
    except Exception as e:
        print(f"Error executing command {' '.join(command)}: {e}")
        return -1, "", str(e)


def validate_patch(issue_id: str, patch_diff: str) -> dict:
    """
    Validates a proposed code patch by applying it and running tests/analysis.

    Args:
        issue_id: The ID of the issue the patch is for.
        patch_diff: The patch in diff format.

    Returns:
        A dictionary containing the validation results (is_valid, test_results,
        linting_results, etc.).
    """
    print(f"🧪 Starting patch validation for issue: {issue_id}")

    repo_info = platform_data_api.get_repository_info_for_issue(issue_id)
    if not repo_info:
        print(f"❌ Validation failed: Repository info not available for issue {issue_id}.")
        return {"is_valid": False, "reason": "Repository not linked."}

    repository_url = repo_info.get("repository_url")
    base_branch = repo_info.get("default_branch", "main")

    # 1. Clone the repository to a temporary local directory
    local_repo_path = platform_data_api.clone_repository(repository_url, base_branch)
    if not local_repo_path or not os.path.exists(local_repo_path):
         print(f"❌ Validation failed: Could not clone repository for issue {issue_id}.")
         return {"is_valid": False, "reason": "Repository cloning failed."}


    # 2. Apply the proposed patch to the local copy
    patch_file_path = None
    try:
        # Save the diff to a temporary file
        patch_file_path = os.path.join(local_repo_path, f"{issue_id}.patch")
        with open(patch_file_path, "w") as f:
            f.write(patch_diff)

        # Apply the patch using git apply command
        # git apply expects to be run in the root of the repository
        return_code, stdout, stderr = run_command_in_repo(["git", "apply", patch_file_path], local_repo_path)

        if return_code != 0:
             print(f"❌ Validation failed: Git apply failed for issue {issue_id}. Stderr:\n{stderr}")
             # Clean up the temporary repository clone
             platform_data_api.cleanup_repository(local_repo_path)
             # Clean up the patch file
             if patch_file_path and os.path.exists(patch_file_path):
                 os.remove(patch_file_path)
             return {"is_valid": False, "reason": f"Patch application failed: {stderr}"}

        print("✅ Patch applied successfully.")

    except Exception as e:
        print(f"❌ Error during patch application for issue {issue_id}: {e}")
        # Clean up resources
        if local_repo_path and os.path.exists(local_repo_path):
            platform_data_api.cleanup_repository(local_repo_path)
        if patch_file_path and os.path.exists(patch_file_path):
            os.remove(patch_file_path)
        return {"is_valid": False, "reason": f"Patch application failed: {e}"}

    finally:
        # Clean up the patch file if it was created
        if patch_file_path and os.path.exists(patch_file_path):
            os.remove(patch_file_path)


    # 3. Run validation steps (tests, linting, static analysis)
    test_results = {"status": "not run", "stdout": "", "stderr": "", "failed_tests": [], "passed_tests": []}
    linting_results = {"status": "not run", "stdout": "", "stderr": "", "violations": []}
    static_analysis_results = {"status": "not run", "stdout": "", "stderr": "", "warnings": []}
    is_valid = False
    validation_reason = "Patch applied. Validation checks pending."

    try:
        # Example: Run tests
        if TEST_COMMAND:
            test_return_code, test_stdout, test_stderr = run_command_in_repo(TEST_COMMAND, local_repo_path)
            test_results["stdout"] = test_stdout
            test_results["stderr"] = test_stderr
            if test_return_code == 0:
                test_results["status"] = "passed"
                # You'll need to parse test_stdout/stderr to get failed/passed tests
                test_results["passed_tests"] = ["(parsing needed)"]
                test_results["failed_tests"] = []
            else:
                test_results["status"] = "failed"
                test_results["failed_tests"] = ["(parsing needed)"]
                test_results["passed_tests"] = ["(parsing needed)"]

        # Example: Run linters
        if LINT_COMMAND:
            lint_return_code, lint_stdout, lint_stderr = run_command_in_repo(LINT_COMMAND, local_repo_path)
            linting_results["stdout"] = lint_stdout
            linting_results["stderr"] = lint_stderr
            if lint_return_code == 0:
                linting_results["status"] = "clean"
                linting_results["violations"] = []
            else:
                linting_results["status"] = "has violations"
                # You'll need to parse lint_stdout/stderr to get violations
                linting_results["violations"] = ["(parsing needed)"]

        # Example: Run static analysis
        if STATIC_ANALYSIS_COMMAND:
            sa_return_code, sa_stdout, sa_stderr = run_command_in_repo(STATIC_ANALYSIS_COMMAND, local_repo_path)
            static_analysis_results["stdout"] = sa_stdout
            static_analysis_results["stderr"] = sa_stderr
            if sa_return_code == 0:
                 static_analysis_results["status"] = "clean"
                 static_analysis_results["warnings"] = []
            else:
                 static_analysis_results["status"] = "has warnings/errors"
                 # You'll need to parse sa_stdout/stderr
                 static_analysis_results["warnings"] = ["(parsing needed)"]


        # Determine if the patch is valid based on results
        if test_results.get("status") == "passed" and linting_results.get("status") != "has violations" and static_analysis_results.get("status") != "has warnings/errors":
             is_valid = True
             validation_reason = "Patch applied successfully, tests passed, and code analysis tools reported no significant issues."
        else:
             is_valid = False
             validation_reason = "Patch applied but validation checks failed (check test, linting, or static analysis results)."


    except Exception as e:
        print(f"❌ Error during validation checks for issue {issue_id}: {e}")
        is_valid = False
        validation_reason = f"Validation checks encountered an error: {e}"
    finally:
        # Clean up the temporary repository clone regardless of validation success
        if local_repo_path and os.path.exists(local_repo_path):
            platform_data_api.cleanup_repository(local_repo_path)


    validation_results = {
        "is_valid": is_valid,
        "reason": validation_reason,
        "test_results": test_results,
        "linting_results": linting_results,
        "static_analysis_results": static_analysis_results
    }

    print(f"✅ Patch validation complete for issue: {issue_id} - Valid: {is_valid}")
    return validation_results

# Example usage (for testing this script directly)
if __name__ == "__main__":
    # This requires a local git executable and potentially test/linting tools
    # Make sure you have a dummy repository for testing.
    # Example:
    # 1. Create a directory: mkdir test_repo && cd test_repo
    # 2. git init
    # 3. echo "def buggy(): return None" > buggy.py
    # 4. git add buggy.py && git commit -m "Add buggy file"
    # 5. Define a mock patch that fixes buggy.py

    # Set up a mock issue in the platform_data_api's mock db
    # Make sure the repository URL points to your local test repo
    platform_data_api.db["ISSUE-VALIDATE-TEST"] = {
        "id": "ISSUE-VALIDATE-TEST",
        "title": "Example: Test validation",
        "description": "Issue to test patch validation.",
        "status": "Patch Suggested",
        "repository": "/path/to/your/local/test_repo", # <--- Update this path
        "relevant_files": ["buggy.py"],
        "logs": "",
        "error_message": "",
        "assigned_to": "autonomous-agent",
        "diagnosis": {},
        "patch_suggestion": {"suggested_patch_diff": """
--- a/buggy.py
+++ b/buggy.py
@@ -1,2 +1,3 @@
 def buggy():
-    return None
+    # This is the fix
+    return "Fixed Value"
"""}
    }
    # You might also need to configure mock commands or create dummy test files
    # in your test_repo to see realistic validation results.


    mock_issue_id = "ISSUE-VALIDATE-TEST" # <--- Use the test issue ID
    mock_patch = platform_data_api.db[mock_issue_id]["patch_suggestion"]["suggested_patch_diff"]
    print(f"Running standalone patch validation for {mock_issue_id}")
    print(f"NOTE: This requires a local git executable and configured test/lint commands.")
    print(f"NOTE: Update the 'repository' path in platform_data_api.db['{mock_issue_id}'] to a local test repo.")

    validation_result = validate_patch(mock_issue_id, mock_patch)
    print("\nValidation Result:")
    import json
    print(json.dumps(validation_result, indent=2))

    # Clean up mock issue
    del platform_data_api.db["ISSUE-VALIDATE-TEST"]
