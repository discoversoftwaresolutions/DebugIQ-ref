import os
import sys
import json
import logging
import argparse
from typing import Optional, Dict

from debugiq_agents.utils import ai_api_client, platform_data_api
from debugiq_agents.core.logger import get_logger

logger = get_logger("agent_review_pr")

def review_pull_request(
    pr_id: str,
    repository_url: str,
    source_branch: str,
    target_branch: str,
    pr_title: str,
    pr_description: str,
    code_diff: str
) -> Optional[Dict[str, str]]:
    """
    Uses the AI agent to perform a structured review of a pull request.

    Returns:
        dict: {
            summary: str,
            potential_issues: str,
            suggestions: str,
            security_concerns: str,
            suggested_tests: str
        }
        or None if error occurs
    """
    logger.info(f"Reviewing PR ID: {pr_id} ({source_branch} -> {target_branch})")

    # --- Fetch Linked Issue (if implemented) ---
    try:
        linked_issue_info = platform_data_api.get_linked_issue(pr_id)
    except Exception as e:
        logger.warning(f"No linked issue info for PR {pr_id}: {e}")
        linked_issue_info = "N/A"

    # --- Build Prompt ---
    prompt = f"""
You are reviewing a pull request.

Repository: {repository_url}
Merging: {source_branch} → {target_branch}
Title: {pr_title}
Description:
{pr_description}

Linked Issue Info: {linked_issue_info}

Code Diff:
```diff
{code_diff}
