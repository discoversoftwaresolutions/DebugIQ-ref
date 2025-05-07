from fastapi import APIRouter
from pydantic import BaseModel
from app.services.gpt4o_agent import run_gpt4o_agent
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
    prompt = f"""You are an autonomous debugging agent. Analyze the following Python traceback and source code.
Output sections using this format:
### PATCH
<corrected source file content>
### EXPLANATION
<description of what was fixed and why>
### SUMMARY
<markdown documentation summary>

Traceback:
{input.trace}

Source Files:
{input.source_files}
"""

    full_response = run_gpt4o_agent(prompt)
    parsed = extract_sections(full_response)

    return AnalyzeResponse(
        patch=parsed.get("PATCH", "# No patch returned"),
        explanation=parsed.get("EXPLANATION", "No explanation provided."),
        doc_summary=parsed.get("SUMMARY", "No summary provided."),
        patched_file_name="main.py",
        original_patched_file_content="print('fix me')"
    )
