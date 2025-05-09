from fastapi import APIRouter
from scripts import platform_data_api

router = APIRouter()

@router.get("/metrics/summary", tags=["Metrics"])
def get_summary_metrics():
    """
    Returns key operational metrics on autonomous fix success rate and throughput.
    """
    return platform_data_api.get_autonomous_fix_metrics()
