# File: DebugIQ-backend/app/api/issues_router.py

from fastapi import APIRouter
from scripts.utils import platform_data_api

router = APIRouter()

@router.get("/issues/inbox", tags=["Issues"])
def get_new_issues():
    """
    Fetches all issues that are newly ingested and not yet processed.
    """
    try:
        issues = platform_data_api.query_issues_by_status("New")
        return {"issues": issues}
    except Exception as e:
        return {"error": str(e), "status": "failed to fetch inbox"}

@router.get("/issues/attention-needed", tags=["Issues"])
def get_issues_needing_attention():
    """
    Returns issues that failed at any stage or require manual intervention.
    """
    try:
        issues = platform_data_api.query_issues_by_status([
            "Diagnosis Failed - AI Analysis",
            "Validation Failed - Manual Review",
            "PR Creation Failed - Needs Review",
            "QA Failed - Needs Review"
        ])
        return {"issues": issues}
    except Exception as e:
        return {"error": str(e), "status": "failed to fetch attention-needed list"}
