# DebugIQ-backend/scripts/agent_suggest_patch.py

import os
from scripts import platform_data_api
# Assuming you have configured API clients in a separate module
# from api_clients import codex_client, gpt4o_client

# --- Configuration ---
# ai_patch_client = codex_client # Or gpt4o_client, based on config

# --- Mock AI Client (Replace with your actual AI client implementation) ---
class MockAIPatchClient:
    def generate_patch(self, prompt: str, code_context: str) -> dict:
        print(">>> Calling Mock AI Patch Generation API...")
        # Simulate processing time and response
        import time
        time.sleep(2)
        # Simulate generating a patch based on the prompt and context
        simulated_diff = """
--- a/path/to/relevant/file.py
+++ b/path/to/relevant/file.py
@@ -XX,Y +XX,Z @@
 # Original buggy code around the area
-    buggy_code()
+    # Check for None before processing
+    data = fetch_data() # Assuming this was called earlier
+    if data is not None:
+        fixed_code = data.process()
+    else:
+        # Handle the None case, e.g., return default, log error, etc.
+        fixed_code = None # Example handling

"""
        simulated_explanation = "The AI generated a patch to add a check for a None value before attempting to access its attributes, based on the diagnosis."

        print("<<< Mock AI Patch Generation API response received.")
        return {"patch_diff": simulated_diff, "explanation": simulated_explanation, "model": "MockCodex"}

ai_patch_client = MockAIPatchClient() # Use the mock client for now

# --- End Mock AI Client ---

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

    # Use suggested_fix_areas from diagnosis to fetch more targeted code context
    files_to_fetch = list(set(diagnosis.get("relevant_files", []) + [area.split("#")[0] for area in diagnosis.get("suggested_fix_areas", []) if "#" in area]))

    if not files_to_fetch:
        print(f"⚠️ No relevant files or suggested areas found in diagnosis for issue {issue_id}. Fetching a default set or failing.")
        # Fallback: try fetching files mentioned in the original issue or fail
        issue_details = platform_data_api.fetch_issue_details(issue_id)
        files_to_fetch = issue_details.get("relevant_files", [])
        if not files_to_fetch:
             print(f"❌ Patch suggestion failed: No files to process for issue {issue_id}.")
             return None


    relevant_code = platform_data_api.fetch_code_context(
        repo_info.get("repository_url"),
        files_to_fetch
    )

    if not relevant_code:
        print(f"❌ Patch suggestion failed: Could not fetch code context for issue {issue_id}.")
        return None

    # 2. Use AI (Codex/GPT-4o) to generate a patch
    # Construct a detailed prompt for the AI model, including diagnosis and code
    patch_prompt = f"""
You are an AI assistant tasked with generating a code patch to fix a software bug.
Here is the diagnosis of the issue:

Root Cause: {diagnosis.get('root_cause', 'Unknown.')}
Detailed Analysis: {diagnosis.get('detailed_analysis', 'No detailed analysis.')}
Suggested Fix Areas: {', '.join(diagnosis.get('suggested_fix_areas', ['None']))}

Here is the relevant code context from the project:
---
{relevant_code}
---

Generate a code patch in the unified diff format (`--- a/... +++ b/...`) that fixes the identified issue.
Provide a brief explanation of the fix.
Only provide the patch and the explanation.
"""

    try:
        # --- Call your actual AI client here ---
        # Example using the mock client:
        ai_patch_response = ai_patch_client.generate_patch(
            prompt=patch_prompt,
            code_context=relevant_code # Pass code context separately if your client supports it
        )
        # --- End Actual AI Client Call ---

        # 3. Process and structure the AI's response
        suggested_patch = {
            "suggested_patch_diff": ai_patch_response.get("patch_diff", "").strip(),
            "explanation": ai_patch_response.get("explanation", "AI did not provide an explanation."),
            "ai_model_used": ai_patch_response.get("model", "Unknown"),
            "raw_ai_output": ai_patch_response # Store full AI response
        }

        # Basic validation: check if a diff was actually generated
        if not suggested_patch["suggested_patch_diff"]:
             print(f"❌ AI did not return a patch diff for issue {issue_id}.")
             return None

        print(f"✅ Patch suggestion complete for issue: {issue_id}")
        return suggested_patch

    except Exception as e:
        print(f"❌ Error during AI patch suggestion for issue {issue_id}: {e}")
        # Log the full traceback in a real application
        return None

# Example usage (for testing this script directly)
if __name__ == "__main__":
    # Set up a mock issue and diagnosis in the platform_data_api's mock db
    platform_data_api.db["ISSUE-PATCH-TEST"] = {
        "id": "ISSUE-PATCH-TEST",
        "title": "Example: Function returns None unexpectedly",
        "description": "A critical function in the data processing module returns None when it should return a valid object, causing subsequent errors.",
        "status": "Diagnosis Complete",
        "repository": "https://github.com/your-org/your-repo.git",
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

    mock_issue_id = "ISSUE-PATCH-TEST"
    mock_diagnosis = platform_data_api.db[mock_issue_id]["diagnosis"]
    print(f"Running standalone patch suggestion for {mock_issue_id}")
    patch_result = agent_suggest_patch(mock_issue_id, mock_diagnosis)
    print("\nPatch Suggestion Result:")
    import json
    print(json.dumps(patch_result, indent=2))

    # Clean up mock code context function
    platform_data_api.fetch_code_context = original_fetch_code_context
    del platform_data_api.db["ISSUE-PATCH-TEST"]
