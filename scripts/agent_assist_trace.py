import os
import sys
import json
import logging
import argparse
from typing import Optional, Dict

from .utils import ai_api_client, platform_data_api

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def assist_trace(
    issue_id: str,
    log_content: Optional[str] = None,
    code_snippet: Optional[str] = None,
    error_message: Optional[str] = None
) -> Optional[Dict[str, any]]:
    """
    Analyze debugging context using the AI agent and provide actionable suggestions.

    Args:
        issue_id (str): Unique ID of the issue.
        log_content (str, optional): Logs surrounding the issue.
        code_snippet (str, optional): Code related to the issue.
        error_message (str, optional): Specific error message.

    Returns:
        dict: Structured result with analysis, suggestions, and confidence.
        None: If analysis fails.
    """
    logging.info(f"[DebugIQ] Agent Assist Trace triggered for Issue ID: {issue_id}")

    try:
        # --- Context Assembly ---
        context_lines = [f"Issue ID: {issue_id}"]
        if error_message:
            context_lines.append(f"Error Message: {error_message}")
        if log_content:
            context_lines.append(f"Relevant Logs:\n{log_content}")
        if code_snippet:
            context_lines.append(f"Code Snippet:\n```\n{code_snippet}\n```")

        # Optionally pull more context from platform
        # TODO: Enrich context with platform metadata
        # issue_details = platform_data_api.fetch_issue_details(issue_id)
        # context_lines.append(f"Environment: {issue_details.get('environment')}")
        full_context = "\n".join(context_lines)

        logging.info("Assembled full context. Querying AI agent...")

        prompt = (
            "Analyze the following software issue context and help identify the root cause. "
            "Provide likely causes, areas to investigate, and suggest initial debugging steps.\n\n"
            f"Context:\n{full_context}\n\nAnalysis:"
        )

        # --- AI Call ---
        response = ai_api_client.chat_completion(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )

        agent_content = response["choices"][0]["message"]["content"]

        # TODO: Optional NLP parsing for deeper structure
        result = {
            "analysis": agent_content,
            "suggestions": "Review code initialization and log input handling as per agent response.",
            "confidence_score": 0.85  # Replace with actual if API supports it
        }

        logging.info("Agent analysis received successfully.")
        return result

    except Exception as e:
        logging.error(f"Agent assist failed: {e}", exc_info=True)
        return None

def parse_args():
    parser = argparse.ArgumentParser(description="Run AI-assisted trace analysis.")
    parser.add_argument("--issue-id", required=True, help="Unique issue ID")
    parser.add_argument("--log-content", help="Logs related to the issue")
    parser.add_argument("--code-snippet", help="Code snippet triggering the issue")
    parser.add_argument("--error-message", help="Specific error message")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    result = assist_trace(
        issue_id=args.issue_id,
        log_content=args.log_content,
        code_snippet=args.code_snippet,
        error_message=args.error_message
    )

    if result:
        print(json.dumps(result, indent=2))
    else:
        sys.exit("Failed to retrieve analysis from agent.")
