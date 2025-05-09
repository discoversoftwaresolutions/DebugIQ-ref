# Re-create platform_data_api.py after environment reset
from pathlib import Path

platform_data_api_code = '''
# scripts/platform_data_api.py

# 🔧 In-memory mock database to simulate platform state
db = {}

def fetch_issue_details(issue_id):
    return db.get(issue_id, {})

def store_diagnosis(issue_id, diagnosis_data):
    db.setdefault(issue_id, {})['diagnosis'] = diagnosis_data

def update_issue_status(issue_id, status):
    db.setdefault(issue_id, {})['status'] = status

def query_issues_by_status(status_filter):
    if isinstance(status_filter, list):
        return {k: v for k, v in db.items() if v.get('status') in status_filter}
    return {k: v for k, v in db.items() if v.get('status') == status_filter}

def get_validation_results(issue_id):
    return db.get(issue_id, {}).get('validation_results', {})

def get_autonomous_fix_metrics():
    total = len(db)
    fixed = sum(1 for i in db.values() if i.get('status') == "PR Created - Awaiting Review/QA")
    return {
        "total_issues": total,
        "autonomous_fixed": fixed,
        "success_rate": round(fixed / total, 2) if total else 0
    }

def get_diagnosis(issue_id):
    return db.get(issue_id, {}).get("diagnosis", {})

def get_proposed_patch(issue_id):
    return db.get(issue_id, {}).get("patch_suggestion", {})

def store_qa_results(issue_id, qa_data):
    db.setdefault(issue_id, {})["qa_results"] = qa_data

def store_validation_results(issue_id, validation_data):
    db.setdefault(issue_id, {})["validation_results"] = validation_data

def create_new_issue(issue_data):
    issue_id = f"ISSUE-{len(db)+1:04d}"
    db[issue_id] = issue_data
    return issue_id

def find_duplicate_issue(structured_issue):
    for issue_id, data in db.items():
        if data.get("summary") == structured_issue.get("summary"):
            return True, issue_id
    return False, None

def update_issue_with_new_data(issue_id, structured_issue):
    db.setdefault(issue_id, {}).update(structured_issue)

def fetch_comprehensive_context(issue_id):
    issue = db.get(issue_id, {})
    return {
        "logs": issue.get("logs", ""),
        "code_snippet": issue.get("code_snippet", ""),
        "meta": issue.get("meta", {})
    }
'''.strip()

platform_data_api_path = Path("/mnt/data/DebugIQ-backend/scripts/platform_data_api.py")
platform_data_api_path.parent.mkdir(parents=True, exist_ok=True)
platform_data_api_path.write_text(platform_data_api_code + "\n")

platform_data_api_path
