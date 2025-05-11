# scripts/agent_suggest_patch.py

import json
import traceback
from scripts import platform_data_api
from scripts.utils.ai_api_clients import call_ai_agent  # ✅ Absolute import with PYTHONPATH=/app

PATCH_SUGGESTION_TASK_TYPE = "patch_suggestion"

def agent_suggest_patch(issue_id: str, diagnosis: dict) -> dict | None:
    """
    Uses AI to suggest a code patch based on the diagnosis.
    """
    print(f"[🩹] Suggesting patch for issue: {issue_id}")

    repo_info = platform_data_api.get_repository_info_for_issue(issue_id)
    if not repo_info:
        print(f"[❌] Repository info not found for issue {issue_id}")
        return None

    files_to_fetch = list(set(
        diagnosis.get("relevant_files", []) +
        [a.split("#")[0] for a in diagnosis.get("suggested_fix_areas", []) if "#" in a]
    ))

    if not files_to_fetch:
        print(f"[⚠️] No relevant files to fetch for {issue_id}")
        return None

    code_context = platform_data_api.fetch_code_context(repo_info["repository_url"], files_to_fetch)
    if not code_context or code_context.strip() == "":
        print(f"[❌] Code context unavailable for {issue_id}")
        return None

    prompt = f"""
You are an AI assistant generating a patch in unified diff format to fix a software bug.

Diagnosis:
- Root Cause: {diagnosis.get('root_cause')}
- Analysis: {diagnosis.get('detailed_analysis')}
- Fix Areas: {', '.join(diagnosis.get('suggested_fix_areas', []))}

Relevant Code:
---
{code_context}
---

Respond only with a unified diff followed by an explanation. Example:
--- a/file.py
+++ b/file.py
@@ -1,1 +1,2 @@
- old code
+ new code

Explanation:
<Your explanation here>
"""

    try:
        response = call_ai_agent(PATCH_SUGGESTION_TASK_TYPE, prompt)

        # Parse as JSON if returned that way, else treat as plain string
        if isinstance(response, str):
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                result = {"patch": response, "explanation": "No structured explanation."}
        else:
            result = response

        return {
            "patch": result.get("patch", ""),
            "explanation": result.get("explanation", "No explanation provided.")
        }

    except Exception as e:
        print(f"[🔥] Error generating patch for {issue_id}: {e}")
        traceback.print_exc()
        return None
