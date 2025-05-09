# Overwrite create_fix_pull_request.py with fully corrected and validated implementation
full_create_fix_code = '''
from pathlib import Path
import os
import sys
import json

from .utils import git_host_api
from .utils import platform_data_api
from .utils import ai_api_client

def create_pull_request(issue_id, branch_name, code_diff, diagnosis_details, validation_results):
    """
    Creates a pull request using AI-generated title and body content.
    """
    print(f"[🚀] Creating PR for Issue {issue_id} from branch '{branch_name}'")

    # Step 1: Use AI to generate PR content
    try:
        print("[🤖] Generating PR title and body using AI...")

        pr_prompt = f\"\"\"
Create a professional Pull Request title and body from the following:

- Issue ID: {issue_id}
- Diagnosis: {json.dumps(diagnosis_details, indent=2)}
- Code Diff:
```diff
{code_diff}
