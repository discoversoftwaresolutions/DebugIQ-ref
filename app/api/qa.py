from fastapi import APIRouter
from pydantic import BaseModel
from app.utils.gpt4o_client import run_gpt4o_chat

router = APIRouter()

class QARequest(BaseModel):
    trace: str
    patch: str
    language: str
    source_files: dict
    patched_file_name: str

class QAResponse(BaseModel):
    llm_qa_result: str
    static_analysis_result: dict

@router.post("/", response_model=QAResponse)
def validate_patch(input: QARequest):
    prompt = f"""You are a QA agent reviewing a patch.
Review the following:

Traceback:
{input.trace}

Patch:
{input.patch}

Files:
{input.source_files}

Answer:
- Does it fix the issue?
- Are there edge cases or bugs?
- Any improvements?

Reply in markdown format.
"""
    result = run_gpt4o_chat("You are a code quality auditor.", prompt)
    static_result = {input.patched_file_name: [{"type": "info", "line": 1, "msg": "Static check placeholder"}]}

    return QAResponse(llm_qa_result=result, static_analysis_result=static_result)
