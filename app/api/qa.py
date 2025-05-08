from fastapi import router
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

@router.post("/qa", response_model=QAResponse)
def validate_patch(input: QARequest):
    prompt = f"""You are reviewing a code patch. Below is the original traceback and the proposed fix. Explain if the patch addresses the issue, and whether it introduces new risks.

Traceback:
{input.trace}

Patch:
{input.patch}
"""
    llm_result = run_gpt4o_chat("You are a senior QA analyst.", prompt)

    static_result = {input.patched_file_name: [{"type": "info", "line": 1, "msg": "Static analysis placeholder"}]}

    return QAResponse(llm_qa_result=llm_result, static_analysis_result=static_result)
