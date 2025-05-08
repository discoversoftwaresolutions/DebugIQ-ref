from fastapi import APIRouter
from pydantic import BaseModel
from app.utils.gpt4o_client import run_gpt4o_chat

router = APIRouter()

class DocRequest(BaseModel):
    patch: str
    explanation: str

class DocResponse(BaseModel):
    doc_summary: str

@router.post("/", response_model=DocResponse)
def generate_doc(input: DocRequest):
    prompt = f"""Document the following patch using markdown.
Patch:
{input.patch}

Explanation:
{input.explanation}

Respond with a clean markdown summary.
"""
    summary = run_gpt4o_chat("You are a senior documentation writer.", prompt)
    return DocResponse(doc_summary=summary)
