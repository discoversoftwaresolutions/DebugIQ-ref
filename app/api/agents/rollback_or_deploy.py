import os
import subprocess
import logging

def rollback():
    print("[⚠️] Rollback triggered. Reverting last commit...")
    subprocess.run(["git", "reset", "--hard", "HEAD~1"], check=True)
    print("[✅] Rollback complete.")

def deploy():
    print("[🚀] Deploying via CI/CD...")
    repo = os.getenv("GITHUB_REPO")
    token = os.getenv("GITHUB_TOKEN")
    workflow_id = os.getenv("DEPLOY_WORKFLOW_ID")
    if repo and token and workflow_id:
        import requests
        response = requests.post(
            f"https://api.github.com/repos/{repo}/actions/workflows/{workflow_id}/dispatches",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json"
            },
            json={"ref": "main"}
        )
        response.raise_for_status()
        print("[✅] Deployment triggered.")
    else:
        print("[❌] Missing required env vars: GITHUB_REPO, GITHUB_TOKEN, DEPLOY_WORKFLOW_ID")

def main():
    report_file = os.getenv("REGRESSION_REPORT", "regression_report.json")
    if os.path.exists(report_file):
        import json
        with open(report_file) as f:
            report = json.load(f)
        if report.get("regressions"):
            rollback()
        else:
            deploy()
    else:
        print("[❌] Regression report not found.")
