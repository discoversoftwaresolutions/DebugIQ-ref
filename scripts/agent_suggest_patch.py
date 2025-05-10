# DebugIQ-backend/scripts/agent_suggest_patch.py

import os
import json
import traceback
from scripts import platform_data_api
from scripts.utils.ai_api_clients import call_ai_agent  # ✅ Corrected import path

# --- Configuration ---
PATCH_SUGGESTION_TASK_TYPE = "patch_suggestion"
# --- End Configuration ---

def agent_suggest_patch(issue_id: str, diagnosis: dict) -> dict | None:
    """
    Uses AI to suggest a code patch based on the diagnosis.
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
        print(f"⚠️ No relevant files or suggested areas found in diagnosis for issue {issue_id}. Cannot suggest a patch.")
        return None

    relevant_code = platform_data_api.fetch_code_context(
        repo_info.get("repository_url"),
        files_to_fetch
    )

    if not relevant_code or relevant_code.strip() == "":
        print(f"❌ Patch suggestion failed: Could not fetch code context or context is empty for issue {issue_id}.")
        return None

    # Construct AI prompt
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
--- a/path/to/file.py
+++ b/path/to/file.py
@@ ... @@
... code changes ...

Explanation:
This patch corrects ...
"""

    try:
        response = call_ai_agent(
            task_type=PATCH_SUGGESTION_TASK_TYPE,
            prompt=patch_prompt
        )

        if not response:
            print(f"❌ No response from AI for issue {issue_id}")
            return None

        response_data = json.loads(response) if isinstance(response, str) else response

        return {
            "patch": response_data.get("patch", ""),
            "explanation": response_data.get("explanation", "No explanation provided.")
        }

    except Exception as e:
        print(f"🔥 Patch suggestion failed for issue {issue_id}: {e}")
        traceback.print_exc()
        return None
