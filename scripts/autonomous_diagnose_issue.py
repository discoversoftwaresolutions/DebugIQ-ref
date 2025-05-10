import os
import json
import traceback
from scripts import platform_data_api
from scripts.utils.ai_api_client import call_ai_agent  # Corrected import

DIAGNOSIS_TASK_TYPE = "diagnosis"

def autonomous_diagnose(issue_id: str) -> dict | None:
    print(f"🔬 Starting autonomous diagnosis for issue: {issue_id}")
    issue_details = platform_data_api.fetch_issue_details(issue_id)
    if not issue_details:
        print(f"❌ Diagnosis failed: Issue {issue_id} not found.")
        return None

    repo_info = platform_data_api.get_repository_info_for_issue(issue_id)
    if not repo_info:
        print(f"⚠️ Repository not linked for issue {issue_id}. Proceeding with diagnosis without code context.")
        code_context = "Repository not linked, code context not available."
    else:
        files_to_fetch = list(set(issue_details.get("relevant_files", [])))
        if not files_to_fetch:
            print(f"⚠️ No specific relevant files for issue {issue_id} mentioned in issue details.")

        code_context = platform_data_api.fetch_code_context(
            repo_info.get("repository_url"),
            files_to_fetch
        )
        if not code_context or code_context.strip() == "":
            print(f"⚠️ Could not fetch code context or context is empty for issue {issue_id}. Proceeding without full context.")
            code_context = "Could not fetch code context or context is empty."

    logs = issue_details.get("logs", "No logs provided.")
    error_message = issue_details.get("error_message", "No specific error message.")
    issue_description = issue_details.get("description", "No description.")
    issue_title = issue_details.get("title", "No title.")

    analysis_prompt = f"""
Analyze the following software issue to determine the root cause.
Provide a JSON with:
"root_cause_summary", "detailed_analysis", "relevant_files", "suggested_areas", "confidence"

Title: {issue_title}
Description: {issue_description}
Error: {error_message}

Logs:
{logs}

Code:
{code_context}
"""

    try:
        print(f"Calling AI for diagnosis (task_type='{DIAGNOSIS_TASK_TYPE}')...")
        ai_raw_response = call_ai_agent(DIAGNOSIS_TASK_TYPE, analysis_prompt)
        print("AI raw response received.")

        if ai_raw_response.strip().startswith("```json"):
            ai_raw_response = ai_raw_response.strip()[len("```json"):].strip()
            if ai_raw_response.endswith("```"):
                ai_raw_response = ai_raw_response[:-len("```")].strip()

        ai_response = json.loads(ai_raw_response)
        if not isinstance(ai_response, dict):
            raise ValueError("AI response is not a dictionary.")

        if not all(key in ai_response for key in ["root_cause_summary", "detailed_analysis", "relevant_files", "suggested_areas", "confidence"]):
            raise ValueError("Missing keys in AI response.")

        diagnosis_details = {
            "root_cause": ai_response.get("root_cause_summary"),
            "detailed_analysis": ai_response.get("detailed_analysis"),
            "relevant_files": list(set(issue_details.get("relevant_files", []) + ai_response.get("relevant_files", []))),
            "suggested_fix_areas": ai_response.get("suggested_areas"),
            "ai_confidence_score": float(ai_response.get("confidence")),
            "raw_ai_output": ai_raw_response
        }

        if diagnosis_details["ai_confidence_score"] < 0.5 or not diagnosis_details["root_cause"]:
            print(f"⚠️ Low confidence or incomplete root cause for issue {issue_id}")
            return None

        print(f"✅ Diagnosis complete for issue: {issue_id}")
        return diagnosis_details

    except Exception as e:
        platform_data_api.update_issue_status(issue_id, "Diagnosis Error")
        print(f"❌ Error during AI diagnosis for issue {issue_id}: {e}")
        traceback.print_exc()
        return None
