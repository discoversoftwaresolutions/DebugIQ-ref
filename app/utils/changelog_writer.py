from datetime import datetime
import os

def append_to_changelog(pr_id, summary, issues, suggestions, path="changelogs/audit_log.md"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(f"## PR {pr_id} – {datetime.utcnow().isoformat()} UTC\n")
        f.write(f"**Summary**: {summary}\n")
        f.write(f"**Issues**: {issues}\n")
        f.write(f"**Suggestions**: {suggestions}\n")
        f.write(f"\n---\n\n")
