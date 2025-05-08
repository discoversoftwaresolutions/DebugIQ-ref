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

def analyze_test_results(
    issue_id: str,
    test_results_content: str,
    code_changes_diff: str
) -> Optional[Dict[str, str]]:
    """
    Analyzes test results alongside code changes using the AI agent.

    Args:
        issue_id (str): Issue identifier.
        test_results_content (str): Test output (JUnit XML, summary, etc.).
        code_changes_diff (str): Unified diff showing code modifications.

    Returns:
        dict: AI-generated insights including test failure analysis and suggestions.
        None: If analysis fails.
    """
    logging.info(f"[DebugIQ] Analyzing test results for Issue ID: {issue_id}")

    try:
        # --- Prompt Construction ---
        prompt = f"""
Analyze the following test results for changes related to Issue ID: {issue_id}.

Code Changes:
```diff
{code_changes_diff}
