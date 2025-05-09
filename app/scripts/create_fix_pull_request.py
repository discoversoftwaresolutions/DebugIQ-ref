# Content for: app/scripts/create_fix_pull_request.py
# (Or your_project_root/scripts/create_fix_pull_request.py)

from pathlib import Path
import os
import sys
import json

# Relative imports - assumes 'utils' is a directory in the same package
# and contains these modules/files.
from .utils import git_host_api
from .utils import platform_data_api
from .utils import ai_api_client

# Note: If this file itself was intended to BE one of the .utils files,
# then the relative imports above would be incorrect.
# Assuming this file is NOT one of the .utils files, but is in a package
# where a 'utils' sibling directory/package exists.

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
        # This is the multi-line f-string definition that needed correct termination
        pr_prompt 
Create a professional Pull Request title and body from the following:

- Issue ID: {issue_id}
- Diagnosis: {json.dumps(diagnosis_details, indent=2)}
- Code Diff:
```diff
{code_diff}
