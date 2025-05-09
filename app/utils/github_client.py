import requests
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def post_pr_comment(repo_full_name: str, pr_number: str, comment_body: str):
    url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    data = {"body": comment_body}
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()
