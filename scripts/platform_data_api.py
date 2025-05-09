# scripts/platform_data_api.py

db = {}  # Simple in-memory mock DB

def fetch_issue_details(issue_id):
    return db.get(issue_id, {})

def store_diagnosis(issue_id, diagnosis_data):
    db.setdefault(issue_id, {})['diagnosis'] = diagnosis_data

def update_issue_status(issue_id, status):
    db.setdefault(issue_id, {})['status'] = status

def query_issues_by_status(status_filter):
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
