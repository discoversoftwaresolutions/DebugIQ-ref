# DebugIQ-backend/scripts/autonomous_diagnose_issue.py

import os
import json # Import json to parse AI response if formatted as JSON
from scripts import platform_data_api
# Import the function to call AI models from your API clients module
# Assuming ai_api_client.py is located directly under /app/ or in a directory in sys.path
from ai_api_client import call_ai_agent # CORRECTED import
import traceback # Import traceback for error logging

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
        # Fetch relevant files if specified in issue or based on initial clues from issue data
        files_to_fetch = list(set(issue_details.get("relevant_files", []))) # Get initial relevant files from issue data
        if not files_to_fetch:
             print(f"⚠️ No specific relevant files for issue {issue_id} mentioned in issue details.")
             # Decide if you want to attempt to fetch a default set of files (e.g., entry points)
             # or rely solely on AI to infer based on logs/description.
             pass # Continue without specific initial files


        # Note: The AI might suggest additional relevant files in its diagnosis,
        # which could be used in a subsequent step before patch generation.
        code_context = platform_data_api.fetch_code_context(
            repo_info.get("repository_url"),
            files_to_fetch
        )
        if not code_context or code_context.strip() == "":
            print(f"⚠️ Could not fetch code context or context is empty for issue {issue_id}. Proceeding with diagnosis without full context.")
            code_context = "Could not fetch code context or context is empty."


    logs = issue_details.get("logs", "No logs provided.")
    error_message = issue_details.get("error_message", "No specific error message.")
    issue_description = issue_details.get("description", "No description.")
    issue_title = issue_details.get("title", "No title.")


    # 2. Use AI (GPT-4o via call_ai_agent) to analyze the information
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
            # Clean up the raw response potentially containing markdown ```json ```
            if ai_raw_response.strip().startswith("```json"):
                 ai_raw_response = ai_raw_response.strip()[len("```json"):].strip()
                 if ai_raw_response.endswith("```"):
                     ai_raw_response = ai_raw_response[:-len("```")].strip()

            ai_response = json.loads(ai_raw_response)
            # Basic validation of expected keys and types
            if not isinstance(ai_response, dict):
                 raise ValueError("AI response is not a dictionary.")
            if not all(key in ai_response and isinstance(ai_response.get(key), expected_type) for key, expected_type in {
                "root_cause_summary": str,
                "detailed_analysis": str,
                "relevant_files": list,
                "suggested_areas": list,
                "confidence": (int, float) # Accept int or float for confidence
            }.items()):
                 # Check lists contain strings
                 if isinstance(ai_response.get("relevant_files"), list) and not all(isinstance(f, str) for f in ai_response.get("relevant_files")):
                     raise ValueError("AI response 'relevant_files' is not a list of strings.")
                 if isinstance(ai_response.get("suggested_areas"), list) and not all(isinstance(a, str) for a in ai_response.get("suggested_areas")):
                     raise ValueError("AI response 'suggested_areas' is not a list of strings.")
                 raise ValueError("AI response missing expected JSON keys or incorrect types.")

        except (json.JSONDecodeError, ValueError) as e:
            print(f"❌ Failed to parse or validate AI response as JSON: {e}")
            print(f"Raw AI response: {ai_raw_response}")
            # Fallback or error handling if AI doesn't return valid JSON
            return {
                "root_cause": "AI response parsing or validation failed.",
                "detailed_analysis": f"Could not parse or validate AI's response. Error: {e}. Raw output: {ai_raw_response}",
                "relevant_files": issue_details.get("relevant_files", []), # Include initial files as fallback
                "suggested_fix_areas": [],
                "ai_confidence_score": 0.0,
                "raw_ai_output": ai_raw_response # Store the raw output for review
            }


        diagnosis_details = {
            "root_cause": ai_response.get("root_cause_summary", "Could not determine root cause."),
            "detailed_analysis": ai_response.get("detailed_analysis", "No detailed analysis from AI."),
            # Combine initial relevant files from issue details with AI suggested files, remove duplicates
            "relevant_files": list(set(issue_details.get("relevant_files", []) + ai_response.get("relevant_files", []))),
            "suggested_fix_areas": ai_response.get("suggested_areas", []),
            "ai_confidence_score": float(ai_response.get("confidence", 0.0)), # Ensure confidence is float
            "raw_ai_output": ai_raw_response # Store the raw output
        }

        # Check if the AI provided a meaningful diagnosis (configurable threshold)
        MIN_CONFIDENCE_THRESHOLD = 0.5 # Define a minimum confidence
        if diagnosis_details.get("ai_confidence_score", 0.0) < MIN_CONFIDENCE_THRESHOLD or (
            not diagnosis_details.get("root_cause") or diagnosis_details.get("root_cause") == "Could not determine root cause."
        ):
             print(f"⚠️ AI diagnosis was low confidence ({diagnosis_details.get('ai_confidence_score', 0.0):.2f}) or inconclusive for issue {issue_id}.")
             # Decide if you want to return None or a low-confidence diagnosis
             # Returning None will stop the workflow based on run_autonomous_workflow's logic
             return None


        print(f"✅ Diagnosis complete for issue: {issue_id}")
        return diagnosis_details

    except Exception as e:
        platform_data_api.update_issue_status(issue_id, "Diagnosis Error") # Update status on error
        print(f"❌ Error during AI diagnosis for issue {issue_id}: {e}")
        traceback.print_exc() # Print full traceback
        return None

# Example usage (for testing this script directly)
if __name__ == "__main__":
    # Set up a mock issue in the platform_data_api's mock db
    # Make sure platform_data_api.py and mock_db.py are accessible/configured
    try:
        from scripts.mock_db import db as mock_db # Assuming you've moved mock_db to a separate file
        platform_data_api.db = mock_db # Link platform_data_api to the mock_db for testing
    except ImportError:
        print("Warning: Could not import mock_db for simulation. Using empty dict.")
        if not hasattr(platform_data_api, 'db'):
             platform_data_api.db = {}


    platform_data_api.db["ISSUE-AI-DIAGNOSIS-TEST"] = {
        "id": "ISSUE-AI-DIAGNOSIS-TEST",
        "title": "Example: Null reference in user module",
        "description": "App crashes when accessing user status.",
        "status": "Open",
        "repository": "https://github.com/your-org/your-repo.git", # Mock repo URL
        "relevant_files": ["src/user.py"], # Initial relevant file
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

    # Temporarily override call_ai_agent for this test to simulate AI response
    original_call_ai_agent = None
    try:
        # Attempt to import the real call_ai_agent to save it
        from ai_api_client import call_ai_agent as real_call_ai_agent
        original_call_ai_agent = real_call_ai_agent

        def simulated_ai_diagnosis_response(task_type, prompt):
             print(">>> Simulating AI Diagnosis API call...")
             # Simulate a realistic JSON response that matches the parsing logic
             simulated_raw_response = """
```json
{
  "root_cause_summary": "Null reference error when accessing user status.",
  "detailed_analysis": "The user object fetched from the database can be None, leading to an attempt to access the 'status' attribute on a None object at line 50 in src/user.py.",
  "relevant_files": ["src/user.py"],
  "suggested_areas": ["src/user.py#L50"],
  "confidence": 0.98
}
