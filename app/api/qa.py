from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class QARequest(BaseModel):
    trace: str
    patch: str
    language: str
    source_files: dict
    patched_file_name: str = None

class QAResponse(BaseModel):
    llm_qa_result: str
    static_analysis_result: dict

@router.post("/", response_model=QAResponse)
def run_qa(input: QARequest):
    return QAResponse(
        llm_qa_result="Patch looks correct and well formatted.",
        static_analysis_result={
            input.patched_file_name or "main.py": [
                {
                    "line": 2,
                    "msg": "Unnecessary pass",
                    "symbol": "unnecessary-pass",
                    "obj": "example_func",
                    "type": "warning"
                }
            ]
        }
    )
