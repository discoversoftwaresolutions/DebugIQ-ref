from fastapi import APIRouter
from pydantic import BaseModel
from app.services.gpt4o_agent import run_gpt4o_agent
from app.utils.parser import extract_sections

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
    prompt = f"""You are a senior code quality agent.
Evaluate the following patch for correctness, quality, and side effects.
Use this format in your response:
### REVIEW
A clear and structured critique of the patch.
### ISSUES
A list of potential concerns or flaws.
### RECOMMENDATIONS
Specific, actionable improvements.

Traceback:
{input.trace}

Patch:
{input.patch}

Source Files:
{input.source_files}
"""

    llm_response = run_gpt4o_agent(prompt)
    sections = extract_sections(llm_response)

    return QAResponse(
        llm_qa_result=sections.get("REVIEW", "No review generated."),
        static_analysis_result={
            input.patched_file_name or "main.py": [
                {
                    "line": 1,
                    "msg": sections.get("ISSUES", "No issues reported."),
                    "symbol": "llm-review",
                    "obj": "autonomous_check",
                    "type": "info"
                }
            ]
        }
    )
