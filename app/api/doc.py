from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class DocRequest(BaseModel):
    code: str
    explanation: str

class DocResponse(BaseModel):
    doc_summary: str

@router.post("/summarize", response_model=DocResponse)
def generate_doc(input: DocRequest):
    # Simulate GPT-4o fine-tuned agent logic
    summary = (
        "### Documentation Summary\n"
        f"This patch introduces the following changes:\n\n{input.explanation}\n\n"
        "The code provided below is intended to reflect the correct behavior after analysis."
    )
    return DocResponse(doc_summary=summary)
