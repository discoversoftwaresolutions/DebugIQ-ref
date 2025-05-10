# DebugIQ-backend/scripts/agent_suggest_patch.py

import os
import json # Import json to parse AI response
from scripts import platform_data_api
# Import the function to call AI models
from api_clients.ai_clients import call_ai_agent # Assuming the above file is in api_clients directory
import traceback # Import traceback for error logging

# --- Configuration ---
# Define the task type for AI calls in this script
PATCH_SUGGESTION_TASK_TYPE = "patch_suggestion"

# --- End Configuration ---

def agent_suggest_patch(issue_id: str, diagnosis: dict) -> dict | None:
    """
    Uses AI to suggest a code patch based on the diagnosis.

    Args:
        issue_id: The ID of the issue.
        diagnosis: The diagnosis details from autonomous_diagnose.

    Returns:
        A dictionary containing the suggested patch diff and explanation,
        or None if patch suggestion fails.
    """
    print(f"🩹 Starting patch suggestion for issue: {issue_id}")

    # 1. Fetch relevant code snippets based on diagnosis
    repo_info = platform_data_api.get_repository_info_for_issue(issue_id)
    if not repo_info:
        print(f"❌ Patch suggestion failed: Repository info not available for issue {issue_id}.")
        return None

    # Use suggested_fix_areas and relevant_files from diagnosis to fetch targeted code context
    files_to_fetch = list(set(diagnosis.get("relevant_files", []) + [area.split("#")[0] for area in diagnosis.get("suggested_fix_areas", []) if "#" in area]))

    if not files_to_fetch:
        print(f"⚠️ No relevant files or suggested areas found in diagnosis for issue {issue_id}. Cannot suggest a patch.")
        return None

    relevant_code = platform_data_api.fetch_code_context(
        repo_info.get("repository_url"),
        files_to_fetch
    )

    if not relevant_code or relevant_code.strip() == "":
        print(f"❌ Patch suggestion failed: Could not fetch code context or context is empty for issue {issue_id}.")
        return None

    # 2. Use AI (GPT-4o) to generate a patch
    # Construct a detailed prompt for the AI model
    # Request the AI to provide the output in a specific format (diff and explanation)
    patch_prompt = f"""
You are an AI assistant tasked with generating a code patch in the unified diff format to fix a software bug.
The user will provide a diagnosis and relevant code context.
Your output must contain ONLY the patch in unified diff format, followed by a brief explanation.
Do not include any other text, introductions, or conclusions outside of the diff and explanation.

Diagnosis:
Root Cause: {diagnosis.get('root_cause', 'Unknown.')}
Detailed Analysis: {diagnosis.get('detailed_analysis', 'No detailed analysis.')}
Suggested Fix Areas: {', '.join(diagnosis.get('suggested_fix_areas', ['None']))}

Relevant Code Context:
---
{relevant_code}
---

Generate the patch in unified diff format, then provide a brief explanation.

Example output format:
```diff
--- a/path/to/file.py
+++ b/path/to/file.py
@@ ... @@
 ... code changes ...
