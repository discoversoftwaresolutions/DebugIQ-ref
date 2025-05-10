import os
import json
import traceback
from typing import Optional, Dict

from scripts import platform_data_api
from scripts.utils.ai_api_clients import call_ai_agent # ✅ Fixed import path based on PYTHONPATH=/app

# --- Configuration ---
PATCH_SUGGESTION_TASK_TYPE = "patch_suggestion"
# --- End Configuration ---


def agent_suggest_patch(issue_id: str, diagnosis: dict) -> Optional[Dict[str, str]]:
    """
    Uses AI to suggest a code patch based on the diagnosis.

    Args:
        issue_id (str): The issue identifier.
        diagnosis (dict): The AI diagnosis dictionary.

    Returns:
        dict: Contains 'patch' and 'explanation' if successful; None otherwise.
    """
    print(f"🩹 Starting patch suggestion for issue: {issue_id}")

    repo_info = platform_data_api.get_repository_info_for_issue(issue_id)
    if not repo_info:
        print(f"❌ Patch suggestion failed: Repository info not available for issue {issue_id}.")
        return None

    files_to_fetch = list(set(
        diagnosis.get("relevant_files", []) +
        [area.split("#")[0] for area in diagnosis.get("suggested_fix_areas", []) if "#" in area]
    ))

    if not files_to_fetch:
        print(f"⚠️ No relevant files or suggested areas found in diagnosis for issue {issue_id}.")
        return None

    relevant_code = platform_data_api.fetch_code_context(
        repo_info.get("repository_url"),
        files_to_fetch
    )

    if not relevant_code or relevant_code.strip() == "":
        print(f"❌ Patch suggestion failed: Empty or unavailable code context for issue {issue_id}.")
        return None

    # --- Prompt Construction ---
    patch_prompt = f"""
You are an AI assistant tasked with generating a code patch in unified diff format to fix a software bug.
The user provides a diagnosis and code context.
Your output must contain ONLY the patch (no markdown) followed by a brief explanation.

Diagnosis:
Root Cause: {diagnosis.get('root_cause', 'Unknown')}
Detailed Analysis: {diagnosis.get('detailed_analysis', 'None')}
Suggested Fix Areas: {', '.join(diagnosis.get('suggested_fix_areas', ['None']))}

Relevant Code Context:
---
{relevant_code}
---

Output Format:
--- a/file.py
+++ b/file.py
@@ -line +line @@
...diff...

Explanation:
This patch fixes ...
"""

    try:
        response = call_ai_agent(
            task_type=PATCH_SUGGESTION_TASK_TYPE,
            prompt=patch_prompt.strip()
        )

        if not response:
            print(f"❌ AI did not return a response for issue {issue_id}")
            return None

        # Parse structured response
        response_data = json.loads(response) if isinstance(response, str) else response

        return {
            "patch": response_data.get("patch", "").strip(),
            "explanation": response_data.get("explanation", "No explanation provided.").strip()
        }

    except Exception as e:
        print(f"🔥 Patch suggestion failed for issue {issue_id}: {e}")
        traceback.print_exc()
        return None
