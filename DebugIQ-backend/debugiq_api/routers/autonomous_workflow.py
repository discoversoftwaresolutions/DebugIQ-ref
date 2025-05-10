# DebugIQ-backend/debugiq_api/routers/autonomous_workflow.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from scripts.run_autonomous_workflow import run_workflow_for_issue

router = APIRouter()

class WorkflowRequest(BaseModel):
    issue_id: str

@router.post("/run_autonomous_workflow")
async def run_autonomous_workflow(request: WorkflowRequest):
    """
    Triggers the full autonomous bug resolution pipeline for a given issue.
    """
    try:
        result = run_workflow_for_issue(request.issue_id)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
