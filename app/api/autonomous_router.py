from fastapi import APIRouter
from pydantic import BaseModel
from scripts import (
    run_autonomous_workflow,
    ingest_and_triage_issue,
    autonomous_diagnose_issue,
    validate_proposed_patch,
    create_fix_pull_request,
    platform_data_api
)

router = APIRouter()

# --- Pydantic Models for Incoming Payloads ---

class IssueInput(BaseModel):
    issue_id: str

class PatchInput(BaseModel):
    issue_id: str
    patch_diff_content: str

class RawIssueData(BaseModel):
    raw_data: dict

# --- Endpoint: Run Full Workflow ---

@router.post("/workflow/run", tags=["Autonomous Agents"])
def run_autonomous(issue: IssueInput):
    """
    Trigger full autonomous workflow for a given issue.
    """
    return run_autonomous_workflow.run_workflow_for_issue(issue.issue_id)

# --- Endpoint: Ingest + Triage New Raw Issue ---

@router.post("/workflow/triage", tags=["Autonomous Agents"])
def triage_issue(payload: RawIssueData):
    """
    AI triages raw issue data (logs, monitoring events, traces).
    """
    return ingest_and_triage_issue.ingest_and_triage(payload.raw_data)

# --- Endpoint: Run Autonomous Diagnosis ---

@router.post("/workflow/diagnose", tags=["Autonomous Agents"])
def diagnose_issue(issue: IssueInput):
    """
    Run AI-powered root cause analysis for an issue.
    """
    return autonomous_diagnose_issue.autonomous_diagnose(issue.issue_id)

# --- Endpoint: Validate a Patch via AI/Tests ---

@router.post("/workflow/validate", tags=["Autonomous Agents"])
def validate_patch(payload: PatchInput):
    """
    Run validation (lint, test, regression check) on patch diff.
    """
    return validate_proposed_patch.validate_patch(
        payload.issue_id,
        payload.patch_diff_content
    )

# --- Endpoint: AI-Generated PR Creation ---

@router.post("/workflow/create-pr", tags=["Autonomous Agents"])
def create_pr(issue: IssueInput):
    """
    Create a PR with an AI-written title/body using diagnosis + validation.
    """
    diagnosis = platform_data_api.get_diagnosis(issue.issue_id)
    patch = platform_data_api.get_proposed_patch(issue.issue_id)
    validation = platform_data_api.get_validation_results(issue.issue_id)

    return create_fix_pull_request.create_pull_request(
        issue_id=issue.issue_id,
        branch_name=f"debugiq/fix-{issue.issue_id.lower()}",
        code_diff=patch.get('suggested_patch_diff', ""),
        diagnosis_details=diagnosis,
        validation_results=validation
    )
