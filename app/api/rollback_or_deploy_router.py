from fastapi import APIRouter
from scripts.rollback_or_deploy import main as deploy_decider

router = APIRouter()

@router.post("/deploy-manager/decide", tags=["Deploy/Rollback"])
def decide_deployment():
    deploy_decider()
    return {"status": "decision_evaluated"}
