@router.get("/issues/{issue_id}/status", tags=["Issues"])
def get_issue_status(issue_id: str):
    """
    Fetches the current status of a specific issue by ID.
    Used by the front-end for live workflow updates.
    """
    try:
        issue = platform_data_api.db.get(issue_id)
        if not issue:
            return {"error": "Issue not found", "issue_id": issue_id, "status": "Not Found"}
        return {
            "issue_id": issue_id,
            "status": issue.get("status", "Unknown")
        }
    except Exception as e:
        return {
            "error": str(e),
            "issue_id": issue_id,
            "status": "Error"
        }
