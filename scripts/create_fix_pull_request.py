# Recreate the path after execution environment reset
from pathlib import Path

create_fix_path = Path("/mnt/data/DebugIQ-backend/scripts/create_fix_pull_request.py")
create_fix_path.parent.mkdir(parents=True, exist_ok=True)

# Write the minimal stub again
stub_code = '''
def create_pull_request(issue_id, branch_name, code_diff, diagnosis_details, validation_results):
    return {
        "url": f"https://mock.github.com/pulls/{issue_id}",
        "title": f"fix({issue_id}): Stub PR",
        "body": f"Autogenerated PR for {issue_id}. Patch:\\n```diff\\n{code_diff}\\n```"
    }
'''.strip()

create_fix_path.write_text(stub_code + "\n")
