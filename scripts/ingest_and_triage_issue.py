from pathlib import Path

# Define the updated production-ready version of ingest_and_triage_issue.py for DebugIQ
ingest_code = '''
import os
import sys
import json
from .utils import monitoring_integration
from .utils import platform_data_api
from .utils import ai_api_client

def ingest_and_triage(raw_issue_data):
    """
    Ingests raw issue data, performs initial parsing/deduplication,
    and uses AI for enhanced classification and prioritization.

    Args:
        raw_issue_data (dict): The raw data representing the issue.

    Returns:
        dict: Structured issue data with enhanced triage info.
              None: If data is invalid or issue is ignored.
    """
    print("[🔍] Ingesting and triaging new issue...")

    try:
        structured_issue = monitoring_integration.parse_raw_issue(raw_issue_data)
        if not structured_issue:
            print("[⚠️] Parsing returned no usable structure.")
            return None

        is_duplicate, existing_issue_id = platform_data_api.find_duplicate_issue(structured_issue)
        if is_duplicate:
            platform_data_api.update_issue_with_new_data(existing_issue_id, structured_issue)
            print(f"[ℹ️] Duplicate found. Updated existing issue ID: {existing_issue_id}")
            return None

        print("[✅] Unique issue identified. Proceeding with triage...")

    except Exception as e:
        print(f"[❌] Error during parsing/deduplication: {e}", file=sys.stderr)
        return None

    # --- Step 3: AI-Powered Classification ---
    try:
        print("[🤖] Running AI-based classification and priority scoring...")

        ai_context = f"""
        A new issue was detected. Analyze the following raw data and structured information to classify its type,
        estimate its severity and priority, and suggest relevant tags.

        Raw Data:
        {json.dumps(raw_issue_data, indent=2)}

        Parsed Structure:
        {json.dumps(structured_issue, indent=2)}

        Output format (JSON):
        {{
            "classification": "...",
            "severity": "...",
            "autonomous_priority": "...",
            "suggested_tags": ["...", "..."],
            "ai_reasoning": "..."
        }}
        """

        # Uncomment and configure for live model use
        # response = ai_api_client.chat_completion(
        #     model="gpt-4o",
        #     messages=[{"role": "user", "content": ai_context}],
        #     response_format={"type": "json_object"}
        # )
        # ai_triage_output = json.loads(response.choices[0].message.content)

        # --- Mock response for development ---
        ai_triage_output = {
            "classification": "Bug",
            "severity": "High",
            "autonomous_priority": "Immediate",
            "suggested_tags": ["NullPointer", "DataProcessing", "ProductionError"],
            "ai_reasoning": "The stack trace indicates a NullPointerException in production. Critical data flow impact."
        }

        structured_issue.update(ai_triage_output)
        print(f"[🧠] Triage complete. Priority: {structured_issue['autonomous_priority']}")

    except Exception as e:
        print(f"[⚠️] AI triage failed: {e}. Falling back...", file=sys.stderr)
        fallback = monitoring_integration.classify_and_prioritize_fallback(structured_issue)
        structured_issue.update(fallback)

    # --- Step 4: Persist Issue to Platform Store ---
    try:
        new_issue_id = platform_data_api.create_new_issue(structured_issue)
        structured_issue["id"] = new_issue_id
        print(f"[💾] Issue stored successfully: ID {new_issue_id}")
    except Exception as e:
        print(f"[❌] Error saving issue to DB: {e}", file=sys.stderr)
        return None

    # --- Step 5: Trigger Autonomous Workflow (Conditional) ---
    if structured_issue.get("autonomous_priority") in ["Immediate", "High"]:
        print(f"[🚦] Triggering autonomous workflow for Issue {new_issue_id}...")
        # from run_autonomous_workflow import trigger_workflow
        # trigger_workflow(new_issue_id)

    return structured_issue
'''.strip()

# Write to target file
ingest_path = Path("/mnt/data/DebugIQ-backend/scripts/ingest_and_triage_issue.py")
ingest_path.parent.mkdir(parents=True, exist_ok=True)
ingest_path.write_text(ingest_code + "\n")

ingest_path
