from fastapi import APIRouter
from scripts.rollback_or_deploy import main as rollback_or_deploy_main

router = APIRouter()

@router.post("/deploy-manager/decide", tags=["DeployManager"])
def deploy_decision():
    """
    Autonomous decision to deploy or rollback based on regression report.
    """
    rollback_or_deploy_main()
    return {"status": "evaluated"}
