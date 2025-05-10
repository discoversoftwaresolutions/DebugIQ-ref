# DebugIQ-backend/scripts/autonomous_diagnose_issue.py

import os
from scripts import platform_data_api
# Assuming you have configured API clients in a separate module
# You will need to implement these clients with actual API calls and error handling
# from api_clients import gemini_client, gpt4o_client

# --- Configuration ---
# Replace with your actual AI client initialization based on configuration
# ai_diagnosis_client = gemini_client # Or gpt4o_client, based on config

# --- Mock AI Client (Replace with your actual AI client implementation) ---
class MockAIDiagnosisClient:
    def analyze(self, prompt: str, code_context: str, logs: str) -> dict:
        print(">>> Calling Mock AI Diagnosis API...")
        # Simulate processing time and response
        import time
        time.sleep(1)
        # In a real implementation, parse the AI model's response carefully
        simulated_response = {
            "root_cause_summary": "Identified a potential null reference issue.",
            "detailed_analysis": f"Based on the logs and code context provided for issue {issue_id}, the AI analyzed the execution flow...",
            "relevant_code_snippets": ["def process_user(user_data): ..."],
            "confidence": 0.9,
            "suggested_areas": ["file.py#L100"],
            "raw_output": {"text": "..."} # Raw output from the AI model
        }
        print("<<< Mock AI Diagnosis API response received.")
        return simulated_response

ai_diagnosis_client = MockAIDiagnosisClient() # Use the mock client for now

# --- End Mock AI Client ---


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
         print(f"❌ Diagnosis failed: Repository not linked for issue {issue_id}.")
         # Attempt diagnosis without code context if repo is missing, though less effective
         code_context = "Repository not linked, code context not available."
    else:
        code_context = platform_data_api.fetch_code_context(
            repo_info.get("repository_url"),
            issue_details.get("relevant_files", []) # Fetch relevant files if specified in issue
        )

    logs = issue_details.get("logs", "No logs provided.")
    error_message = issue_details.get("error_message", "No specific error message.")
    issue_description = issue_details.get("description", "No description.")
    issue_title = issue_details.get("title", "No title.")


    # 2. Use AI (Gemini/GPT-4o) to analyze the information
    # Construct a detailed prompt for the AI model
    analysis_prompt = f"""
Analyze the following software issue to determine the root cause.
Consider the issue title, description, error message, provided logs, and relevant code context.

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

Based on this information, provide a concise summary of the root cause,
a more detailed analysis, identify the most relevant code snippets or files,
suggest specific areas in the code that likely need fixing (e.g., file.py#L123),
and provide a confidence score for your diagnosis (0.0 to 1.0).
Format the response as a JSON object with keys: "root_cause_summary", "detailed_analysis",
"relevant_code_snippets", "confidence", "suggested_areas".
"""

    try:
        # --- Call your actual AI client here ---
        # Example using the mock client:
        ai_response = ai_diagnosis_client.analyze(
            prompt=analysis_prompt,
            code_context=code_context, # Provide code context separately if your client supports it
            logs=logs # Provide logs separately if your client supports it
        )
        # --- End Actual AI Client Call ---

        # 3. Process and structure the AI's response
        # You might need to add robust parsing here to handle variations in AI output
        diagnosis_details = {
            "root_cause": ai_response.get("root_cause_summary", "Could not determine root cause."),
            "detailed_analysis": ai_response.get("detailed_analysis", "No detailed analysis from AI."),
            "relevant_files": issue_details.get("relevant_files", []) + ai_response.get("relevant_code_snippets", []), # Combine initial files with AI suggested
            "suggested_fix_areas": ai_response.get("suggested_areas", []),
            "ai_confidence_score": ai_response.get("confidence", 0.0),
            "raw_ai_output": ai_response # Store the full AI response for debugging/review
        }

        # Simple check if the AI provided a meaningful diagnosis
        if diagnosis_details.get("root_cause") == "Could not determine root cause." and not diagnosis_details.get("suggested_fix_areas"):
             print(f"❌ AI diagnosis was inconclusive for issue {issue_id}.")
             return None


        print(f"✅ Diagnosis complete for issue: {issue_id}")
        return diagnosis_details

    except Exception as e:
        print(f"❌ Error during AI diagnosis for issue {issue_id}: {e}")
        # Log the full traceback in a real application
        return None

# Example usage (for testing this script directly)
if __name__ == "__main__":
    # Set up a mock issue in the platform_data_api's mock db
    platform_data_api.db["ISSUE-TEST"] = {
        "id": "ISSUE-TEST",
        "title": "Example: Function returns None unexpectedly",
        "description": "A critical function in the data processing module returns None when it should return a valid object, causing subsequent errors.",
        "status": "Open",
        "repository": "https://github.com/your-org/your-repo.git",
        "relevant_files": ["src/data_processor.py"],
        "logs": "Error in data_processor.py at line 50: 'NoneType' object has no attribute 'process'",
        "error_message": "'NoneType' object has no attribute 'process'",
        "assigned_to": "autonomous-agent",
    }
    # Add mock code content for fetch_code_context to return
    original_fetch_code_context = platform_data_api.fetch_code_context
    def mock_fetch_code_context(repo_url, file_paths):
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
    platform_data_api.fetch_code_context = mock_fetch_code_context


    mock_issue_id = "ISSUE-TEST"
    print(f"Running standalone diagnosis for {mock_issue_id}")
    diagnosis_result = autonomous_diagnose(mock_issue_id)
    print("\nDiagnosis Result:")
    import json
    print(json.dumps(diagnosis_result, indent=2))

    # Clean up mock code context function
    platform_data_api.fetch_code_context = original_fetch_code_context
    del platform_data_api.db["ISSUE-TEST"]
