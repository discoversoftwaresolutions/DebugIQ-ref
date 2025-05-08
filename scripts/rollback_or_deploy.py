import os
import subprocess
import logging
from debugiq_agents.core.logger import get_logger

logger = get_logger("rollback_or_deploy")

def rollback():
    logger.warning("Initiating rollback: reverting last commit.")
    subprocess.run(["git", "reset", "--hard", "HEAD~1"], check=True)
    logger.info("Rollback complete.")

def deploy():
    logger.info("Triggering deployment via CI/CD.")
    repo = os.getenv("GITHUB_REPO")
    token = os.getenv("GITHUB_TOKEN")
    workflow_id = os.getenv("DEPLOY_WORKFLOW_ID")
    if repo and token and workflow_id:
        import requests
        resp = requests.post(
            f"https://api.github.com/repos/{repo}/actions/workflows/{workflow_id}/dispatches",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json"
            },
            json={"ref": "main"}
        )
        resp.raise_for_status()
        logger.info("Deployment workflow triggered.")
    else:
        logger.error("Missing GITHUB_REPO, GITHUB_TOKEN, or DEPLOY_WORKFLOW_ID env vars.")

def main():
    report_file = os.getenv("REGRESSION_REPORT", "regression_report.json")
    if os.path.exists(report_file):
        with open(report_file) as f:
            report = json.load(f)
        if report.get("regressions"):
            rollback()
        else:
            deploy()
    else:
        logger.error(f"No regression report found at {report_file}, aborting.")

if __name__ == "__main__":
    main()
