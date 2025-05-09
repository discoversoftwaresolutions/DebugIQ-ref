from fastapi import APIRouter
from scripts import platform_data_api

router = APIRouter()

@router.get("/issues/inbox", tags=["Issues"])
def get_new_issues():
    """
    Fetches all issues that are newly ingested and not yet processed.
    """
    return platform_data_api.query_issues_by_status("New")

@router.get("/issues/attention-needed", tags=["Issues"])
def get_issues_needing_attention():
    """
    Returns issues that failed at any stage or require manual intervention.
    """
    return platform_data_api.query_issues_by_status([
        "Diagnosis Failed - AI Analysis",
        "Validation Failed - Manual Review",
        "PR Creation Failed - Needs Review",
        "QA Failed - Needs Review"
    ])
