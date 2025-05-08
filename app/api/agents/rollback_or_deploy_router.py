from pathlib import router

rollback_router_code = '''
from fastapi import APIRouter
from scripts.rollback_or_deploy import main as rollback_or_deploy_main

router = APIRouter()

@router.post("/deploy-manager/decide", tags=["Deploy Manager"])
def deploy_decision():
    """
    Autonomous decision to deploy or rollback based on regression report.
    """
    rollback_or_deploy_main()
    return {"status": "evaluated"}
'''.strip()

router_path = Path("/mnt/data/DebugIQ-backend/app/api/agents/rollback_or_deploy_router.py")
router_path.parent.mkdir(parents=True, exist_ok=True)
router_path.write_text(rollback_router_code + "\n")

router_path
