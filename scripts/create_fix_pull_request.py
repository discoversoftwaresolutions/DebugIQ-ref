from pathlib import Path # Imported but not used in the function below
import os # Imported but not used
import sys # Imported but not used
import json

# Relative imports - assumes 'utils' is a directory in the same package
from .utils import git_host_api
from .utils import platform_data_api # Assumes platform_data_api.py exists in the 'utils' directory
from .utils import ai_api_client # Assumes ai_api_client.py exists in the 'utils' directory

# Note: If this file itself is platform_data_api.py, the import above is wrong.
# Assuming this file is NOT platform_data_api.py.

def create_pull_request(issue_id, branch_name, code_diff, diagnosis_details, validation_results):
    """
    Creates a pull request using AI-generated title and body content.

    Args:
        issue_id (str): The ID of the issue related to the PR.
        branch_name (str): The name of the branch containing the fix.
        code_diff (str): The diff content of the patch.
        diagnosis_details (dict): Output from autonomous diagnosis.
        validation_results (dict): Patch validation results.

    Returns:
        dict: Git host PR metadata or None if failed.
    """
    print(f"[🚀] Creating PR for Issue {issue_id} from branch '{branch_name}'")

    # Step 1: Use AI to generate PR content
    try:
        print("[🤖] Generating PR title and body using AI...")
        pr_prompt = f"""
Create a professional Pull Request title and body from the following:

- Issue ID: {issue_id}
- Diagnosis: {json.dumps(diagnosis_details, indent=2)}
- Code Diff:
```diff
{code_diff}
