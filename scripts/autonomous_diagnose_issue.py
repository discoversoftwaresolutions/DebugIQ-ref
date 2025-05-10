# DebugIQ-backend/scripts/autonomous_diagnose_issue.py

import os
import json # Import json to parse AI response if formatted as JSON
from scripts import platform_data_api
# Import the function to call AI models
# from api_clients.ai_clients import call_ai_agent # Assuming the above file is in api_clients directory
from api_clients.ai_api_client import call_ai_agent # Corrected import
# --- Configuration ---
# Define the task type for AI calls in this script
DIAGNOSIS_TASK_TYPE = "diagnosis"

# --- End Configuration ---


def autonomous_diagnose(issue_id: str) -> dict | None:
    """
    Automatically diagnoses the root cause of a software issue using AI.

    Args:
        issue_id: The ID of the issue to diagnose.

    Returns:
        A dictionary containing the diagnosis details (root cause, relevant files,
        suggested areas for fix) or None if diagnosis fails.
    """
    print(f"🔬 Starting autonomous diagnosis for issue: {issue_id}")

    # 1. Fetch issue details and relevant context (code snippets, logs, etc.)
    issue_details = platform_data_api.fetch_issue_details(issue_id)
    if not issue_details:
        print(f"❌ Diagnosis failed: Issue {issue_id} not found.")
        return None

    repo_info = platform_data_api.get_repository_info_for_issue(issue_id)
    if not repo_info:
         print(f"⚠️ Repository not linked for issue {issue_id}. Proceeding with diagnosis without code context.")
         code_context = "Repository not linked, code context not available."
    else:
        # Fetch relevant files if specified in issue or based on initial clues
        files_to_fetch = issue_details.get("relevant_files", [])
        if not files_to_fetch:
             print(f"⚠️ No specific relevant files for issue {issue_id}. AI might need to infer.")
             # You might add logic here to ask AI which files are relevant based on description/logs
             pass # Continue without specific files or fetch a default set if needed

        code_context = platform_data_api.fetch_code_context(
            repo_info.get("repository_url"),
            files_to_fetch
        )
        if not code_context:
            print(f"⚠️ Could not fetch code context for issue {issue_id}. Proceeding with diagnosis without full context.")
            code_context = "Could not fetch code context."


    logs = issue_details.get("logs", "No logs provided.")
    error_message = issue_details.get("error_message", "No specific error message.")
    issue_description = issue_details.get("description", "No description.")
    issue_title = issue_details.get("title", "No title.")


    # 2. Use AI (GPT-4o) to analyze the information
    # Construct a detailed prompt for the AI model
    # Request the AI to provide the output in JSON format for easier parsing
    analysis_prompt = f"""
Analyze the following software issue to determine the root cause.
Consider the issue title, description, error message, provided logs, and relevant code context.
Provide a concise summary of the root cause, a more detailed analysis,
identify the most relevant file paths or code snippets, suggest specific areas in the code
that likely need fixing (e.g., file.py#L123 format), and provide a confidence score for your diagnosis (0.0 to 1.0).
Format the response strictly as a JSON object with the following keys:
"root_cause_summary": string,
"detailed_analysis": string,
"relevant_files": list of strings (file paths),
"suggested_areas": list of strings (file.py#Linenumber),
"confidence": float (0.0 to 1.0)

Issue Title: {issue_title}
Issue Description: {issue_description}
Error Message: {error_message}

Logs:
---
{logs}
---

Relevant Code Context:
---
{code_context}
---
"""

    try:
        # --- Call the AI agent for diagnosis ---
        print(f"Calling AI for diagnosis (task_type='{DIAGNOSIS_TASK_TYPE}')...")
        ai_raw_response = call_ai_agent(DIAGNOSIS_TASK_TYPE, analysis_prompt)
        print("AI raw response received.")
        # --- End AI Call ---

        # 3. Process and structure the AI's response
        # Attempt to parse the expected JSON output from the AI
        try:
            ai_response = json.loads(ai_raw_response)
            # Basic validation of expected keys
            if not all(key in ai_response for key in ["root_cause_summary", "detailed_analysis", "relevant_files", "suggested_areas", "confidence"]):
                 raise ValueError("AI response missing expected JSON keys.")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"❌ Failed to parse AI response as JSON: {e}")
            print(f"Raw AI response: {ai_raw_response}")
            # Fallback or error handling if AI doesn't return valid JSON
            return {
                "root_cause": "AI response parsing failed.",
                "detailed_analysis": f"Could not parse AI's response. Raw output: {ai_raw_response}",
                "relevant_files": issue_details.get("relevant_files", []),
                "suggested_fix_areas": [],
                "ai_confidence_score": 0.0,
                "raw_ai_output": ai_raw_response # Store the raw output for review
            }


        diagnosis_details = {
            "root_cause": ai_response.get("root_cause_summary", "Could not determine root cause."),
            "detailed_analysis": ai_response.get("detailed_analysis", "No detailed analysis from AI."),
            # Combine initial relevant files with AI suggested files, remove duplicates
            "relevant_files": list(set(issue_details.get("relevant_files", []) + ai_response.get("relevant_files", []))),
            "suggested_fix_areas": ai_response.get("suggested_areas", []),
            "ai_confidence_score": ai_response.get("confidence", 0.0),
            "raw_ai_output": ai_raw_response # Store the raw output
        }

        # Check if the AI provided a meaningful diagnosis
        if diagnosis_details.get("ai_confidence_score", 0.0) < 0.5 and not diagnosis_details.get("suggested_fix_areas"):
             print(f"⚠️ AI diagnosis was low confidence and inconclusive for issue {issue_id}.")
             # Decide if you want to return None or a low-confidence diagnosis
             # Returning None will stop the workflow based on run_autonomous_workflow's logic
             return None


        print(f"✅ Diagnosis complete for issue: {issue_id}")
        return diagnosis_details

    except Exception as e:
        print(f"❌ Error during AI diagnosis for issue {issue_id}: {e}")
        traceback.print_exc() # Print full traceback
        return None

# Example usage (for testing this script directly)
if __name__ == "__main__":
    # Set up a mock issue in the platform_data_api's mock db
    platform_data_api.db["ISSUE-AI-DIAGNOSIS-TEST"] = {
        "id": "ISSUE-AI-DIAGNOSIS-TEST",
        "title": "Example: Null reference in user module",
        "description": "App crashes when accessing user status.",
        "status": "Open",
        "repository": "https://github.com/your-org/your-repo.git", # Mock repo
        "relevant_files": ["src/user.py"],
        "logs": "TypeError: Cannot read property 'status' of null at src/user.py:50",
        "error_message": "Cannot read property 'status' of null",
        "assigned_to": "autonomous-agent",
    }
     # Add mock code context for fetch_code_context
    original_fetch_code_context = platform_data_api.fetch_code_context
    def mock_fetch_code_context_diag(repo_url, file_paths):
         if "src/user.py" in file_paths:
              return """
# src/user.py
class User:
    def __init__(self, status):
        self.status = status

def get_user_status(user_id):
    user = fetch_user_from_db(user_id) # Assume this can return None
    # Bug: Accessing status without checking if user is None
    return user.status # Line 50
"""
         return original_fetch_code_context(repo_url, file_paths)
    platform_data_api.fetch_code_context = mock_fetch_code_context_diag


    mock_issue_id = "ISSUE-AI-DIAGNOSIS-TEST"
    print(f"Running standalone AI diagnosis for {mock_issue_id}")
    diagnosis_result = autonomous_diagnose(mock_issue_id)
    print("\nDiagnosis Result:")
    import json
    print(json.dumps(diagnosis_result, indent=2))

    # Clean up mock code context function and db entry
    platform_data_api.fetch_code_context = original_fetch_code_context
    del platform_data_api.db["ISSUE-AI-DIAGNOSIS-TEST"]
