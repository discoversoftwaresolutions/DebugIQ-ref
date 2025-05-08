from fastapi import APIRouter
from scripts.regression_monitor import main as monitor_main

router = APIRouter()

@router.post("/regression-monitor/run", tags=["Regression"])
def run_monitor():
    monitor_main()
    return {"status": "monitor_completed"}
