from fastapi import APIRouter
from pydantic import BaseModel
from scripts.fix_memory import record_fix

router = APIRouter()

class FixRecord(BaseModel):
    issue_id: str
    trace: str
    patch_diff: str
    validation_feedback: str

@router.post("/fix-memory/record", tags=["Fix Memory"])
def record_fix_endpoint(payload: FixRecord):
    record_fix(
        issue_id=payload.issue_id,
        trace=payload.trace,
        patch_diff=payload.patch_diff,
        validation_feedback=payload.validation_feedback
    )
    return {"status": "success", "message": f"Fix for {payload.issue_id} recorded."}
