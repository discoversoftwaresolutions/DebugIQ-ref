# DebugIQ-backend/scripts/agent_suggest_patch.py

import os
import json
from scripts import platform_data_api
# Import the function to call AI models from your API clients module
from api_clients.ai_api_client import call_ai_agent # Corrected import
import traceback # Import traceback for error logging

# --- Configuration ---
# Define the task type for AI calls in this script
PATCH_SUGGESTION_TASK_TYPE = "patch_suggestion" # Use a distinct task type for routing

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
    # Ensure uniqueness and handle cases where areas might not have a file#line format
    files_to_fetch = list(set(diagnosis.get("relevant_files", []) + [area.split("#")[0] for area in diagnosis.get("suggested_fix_areas", []) if isinstance(area, str) and "#" in area]))

    if not files_to_fetch:
        print(f"⚠️ No relevant files or suggested areas found in diagnosis for issue {issue_id}. Cannot suggest a patch.")
        # Optionally, attempt to fetch files mentioned in the original issue if diagnosis provided none
        issue_details = platform_data_api.fetch_issue_details(issue_id)
        files_to_fetch = list(set(issue_details.get("relevant_files", []))) # Use set to avoid duplicates
        if not files_to_fetch:
             print(f"❌ Patch suggestion failed: No files to process for issue {issue_id} based on diagnosis or issue details.")
             return None
        else:
             print(f"Attempting to fetch files from issue details as diagnosis provided none: {files_to_fetch}")


    relevant_code = platform_data_api.fetch_code_context(
        repo_info.get("repository_url"),
        files_to_fetch
    )

    if not relevant_code or relevant_code.strip() == "":
        print(f"❌ Patch suggestion failed: Could not fetch code context or context is empty for issue {issue_id}.")
        return None

    # 2. Use AI (GPT-4o via call_ai_agent) to generate a patch
    # Construct a detailed prompt for the AI model
    # Request the AI to provide the output in a specific format (diff and explanation)
    # Use clear markers to separate the diff and explanation for parsing
    patch_prompt = f"""
You are an AI assistant tasked with generating a code patch in the unified diff format to fix a software bug.
The user will provide a diagnosis and relevant code context.
Your output must contain ONLY the patch in unified diff format, followed by a brief explanation.
Start the patch with ```diff and end with ```.
After the patch, include "Explanation:" followed by your explanation.

Diagnosis:
Root Cause: {diagnosis.get('root_cause', 'Unknown.')}
Detailed Analysis: {diagnosis.get('detailed_analysis', 'No detailed analysis.')}
Suggested Fix Areas: {', '.join(diagnosis.get('suggested_fix_areas', ['None']))}

Relevant Code Context:
---
{relevant_code}
---

Generate the patch in unified diff format, then provide a brief explanation starting with "Explanation:".
"""

    try:
        # --- Call the AI agent for patch suggestion ---
        print(f"Calling AI for patch suggestion (task_type='{PATCH_SUGGESTION_TASK_TYPE}')...")
        ai_raw_response = call_ai_agent(PATCH_SUGGESTION_TASK_TYPE, patch_prompt)
        print("AI raw response received.")
        # --- End AI Call ---

        # 3. Process and structure the AI's response
        # Attempt to parse the diff and explanation from the raw text response
        suggested_patch_diff = ""
        explanation = "AI did not provide an explanation or parsing failed."

        # Look for the start and end of the diff block (```diff ... ```)
        diff_start_marker = "```diff"
        diff_end_marker = "```"
        explanation_marker = "Explanation:"

        diff_start = ai_raw_response.find(diff_start_marker)
        diff_end = -1
        if diff_start != -1:
             diff_end = ai_raw_response.find(diff_end_marker, diff_start + len(diff_start_marker))


        if diff_start != -1 and diff_end != -1:
            # Extract the text within the diff block
            suggested_patch_diff = ai_raw_response[diff_start + len(diff_start_marker):diff_end].strip()

            # Look for the explanation marker after the diff block
            explanation_start = ai_raw_response.find(explanation_marker, diff_end + len(diff_end_marker))
            if explanation_start != -1:
                # Extract the text after the explanation marker
                explanation = ai_raw_response[explanation_start + len(explanation_marker):].strip()
            else:
                 # If explanation marker not found, the rest of the text after the diff is the explanation
                 explanation = ai_raw_response[diff_end + len(diff_end_marker):].strip()
                 if not explanation: # If there's no text after the diff
                      explanation = "Explanation not found in AI response."


        else:
             explanation = f"Could not find diff block ({diff_start_marker} ... {diff_end_marker}) in AI response. Raw output: {ai_raw_response}"
             print(f"❌ Could not find diff block in AI response for issue {issue_id}.")
             print(f"Raw AI response: {ai_raw_response}")


        # Basic validation: check if a diff was actually generated
        if not suggested_patch_diff:
             print(f"❌ AI did not return a patch diff for issue {issue_id}.")
             return None


        suggested_patch = {
            "suggested_patch_diff": suggested_patch_diff,
            "explanation": explanation,
            # Note: ai_api_client.call_ai_agent returns a string, so model info might need
            # to be added here if your ai_api_client can provide it separately.
            "ai_model_used": "GPT-4o (via call_ai_agent)", # Indicate the model used
            "raw_ai_output": ai_raw_response # Store full AI response
        }

        print(f"✅ Patch suggestion complete for issue: {issue_id}")
        return suggested_patch

    except Exception as e:
        print(f"❌ Error during AI patch suggestion for issue {issue_id}: {e}")
        traceback.print_exc() # Print full traceback
        return None

# Example usage (for testing this script directly)
if __name__ == "__main__":
    # Set up a mock issue and diagnosis in the platform_data_api's mock db
    # Make sure platform_data_api.py is accessible and has mock_db defined or a real DB configured
    try:
        from scripts.mock_db import db as mock_db # Assuming you've moved mock_db to a separate file
        platform_data_api.db = mock_db # Link platform_data_api to the mock_db for testing
    except ImportError:
        print("Could not import mock_db. Please ensure mock_db.py exists or platform_data_api uses a real DB.")
        # Define a minimal mock_db if import fails, just for this test
        if not hasattr(platform_data_api, 'db'):
             platform_data_api.db = {}


    platform_data_api.db["ISSUE-AI-PATCH-TEST"] = {
        "id": "ISSUE-AI-PATCH-TEST",
        "title": "Example: Function returns None unexpectedly",
        "description": "A critical function in the data processing module returns None when it should return a valid object, causing subsequent errors.",
        "status": "Diagnosis Complete",
        "repository": "https://github.com/your-org/your-repo.git", # Mock repo URL
        "relevant_files": ["src/data_processor.py"],
        "logs": "Error in data_processor.py at line 50: 'NoneType' object has no attribute 'process'",
        "error_message": "'NoneType' object has no attribute 'process'",
        "assigned_to": "autonomous-agent",
        "diagnosis": {
            "root_cause": "Function fetch_data() can return None, but process_data() does not handle this.",
            "detailed_analysis": "The AI found that fetch_data does not guarantee a non-None return, leading to an exception in process_data.",
            "relevant_files": ["src/data_processor.py"],
            "suggested_fix_areas": ["src/data_processor.py#L50"],
            "ai_confidence_score": 0.95,
            "raw_ai_output": {}
        }
    }
    # Add mock code content for fetch_code_context to return
    original_fetch_code_context = platform_data_api.fetch_code_context
    def mock_fetch_code_context_patch(repo_url, file_paths):
         if "src/data_processor.py" in file_paths:
              return """
# src/data_processor.py
def fetch_data():
    # Assume this sometimes returns None due to an external dependency issue
    return None

def process_data():
    data = fetch_data()
    # The bug is here, data can be None
    processed = data.process() # This line throws an error
    return processed
"""
         return original_fetch_code_context(repo_url, file_paths)
    platform_data_api.fetch_code_context = mock_fetch_code_context_patch

    mock_issue_id = "ISSUE-AI-PATCH-TEST"
    mock_diagnosis = platform_data_api.db[mock_issue_id]["diagnosis"]
    print(f"Running standalone patch suggestion for {mock_issue_id}")

    # Temporarily override call_ai_agent for this test to simulate AI response
    # This is necessary because we don't want to make a real AI call during a script test
    original_call_ai_agent = None
    try:
        from api_clients.ai_api_client import call_ai_agent as real_call_ai_agent
        original_call_ai_agent = real_call_ai_agent # Store the real function

        def simulated_ai_patch_response(task_type, prompt):
             print(">>> Simulating AI Patch Generation API call...")
             # Simulate a realistic looking diff and explanation that matches the parsing logic
             simulated_raw_response = """
Some introductory text before the diff.

```diff
--- a/src/data_processor.py
+++ b/src/data_processor.py
@@ -4,6 +4,8 @@
 def process_data():
     data = fetch_data()
     # The bug is here, data can be None
-    processed = data.process() # This line throws an error
-    return processed
+    if data is not None:
+        processed = data.process()
+        return processed
+    # Handle the case where data is None - return None or raise error
+    return None # Example: return None when data is None
