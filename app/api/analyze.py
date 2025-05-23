from fastapi import APIRouter
from pydantic import BaseModel
from app.utils.gpt4o_client import run_gpt4o_chat
from app.utils.parser import extract_sections

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
    prompt = f"""You are an autonomous debugging agent.
Analyze the following traceback and source files.
Output the following sections:

### PATCH
<corrected source code>

### EXPLANATION
<why you made these changes>

### SUMMARY
<markdown documentation for the patch>

Traceback:
{input.trace}

Source Files:
{input.source_files}
"""

    result = run_gpt4o_chat("You are a debugging agent for code intelligence.", prompt)
    parsed = extract_sections(result)

    return AnalyzeResponse(
        patch=parsed.get("PATCH", "# No patch returned"),
        explanation=parsed.get("EXPLANATION", "No explanation provided."),
        doc_summary=parsed.get("SUMMARY", "No summary provided."),
        patched_file_name="main.py",
        original_patched_file_content="print('fix me')"
    )
