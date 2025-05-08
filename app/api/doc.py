from fastapi import router
from pydantic import BaseModel
from app.utils.gpt4o_client import run_gpt4o_chat

router = APIRouter()

class DocRequest(BaseModel):
    patch: str
    explanation: str

class DocResponse(BaseModel):
    doc_summary: str

@router.post("/doc", response_model=DocResponse)
def generate_doc(input: DocRequest):
    prompt = f"""Summarize the following patch and explanation into a clear documentation section.

### PATCH
{input.patch}

### EXPLANATION
{input.explanation}
"""
    summary = run_gpt4o_chat("You are a technical writer generating patch documentation.", prompt)
    return DocResponse(doc_summary=summary)
