from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class AnalyzeRequest(BaseModel):
    trace: str
    language: str
    config: dict
    source_files: dict

class AnalyzeResponse(BaseModel):
    patch: str
    explanation: str
    doc_summary: str
    patched_file_name: str
    original_patched_file_content: str

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_code(input: AnalyzeRequest):
    return AnalyzeResponse(
        patch="# Example patch\nprint('fixed')",
        explanation="This fixes a missing print statement.",
        doc_summary="Patched issue where output was not printed.",
        patched_file_name="main.py",
        original_patched_file_content="print('fix me')"
    )
