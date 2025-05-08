# DebugIQ-backend/app/schemas.py
from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Any

# Schema for fetching API endpoints from the backend config router
class ApiEndpoints(BaseModel):
    analyze: str
    qa: str
    doc: str
    voice_transcribe: str
    voice_command: str
    voice_speak: str
    # Add other endpoint fields here if needed

# Schema for the Analyze endpoint request body
class AnalyzeRequest(BaseModel):
    trace: Optional[str] = None # Allow trace to be optional
    language: str = "python"    # Default language to python
    config: Dict[str, Any] = Field(default_factory=dict) # Config dictionary, default to empty dict
    source_files: Dict[str, str] = Field(default_factory=dict) # Dictionary of filenames to content, default to empty dict

# Schema for the Analyze endpoint response body
class AnalyzeResponse(BaseModel):
    patch: str = "# No patch returned" # Default value if missing
    explanation: str = "No explanation provided." # Default value
    doc_summary: str = "No summary provided." # Default value
    # These should ideally be determined by the backend
    patched_file_name: str = "N/A"
    original_patched_file_content: str = "# Original content not provided by backend"

# Schema for the Voice Command request body
class CommandRequest(BaseModel):
    text_command: str

# Schema for the Voice Command response body (assuming text response)
class CommandResponse(BaseModel):
     spoken_text: str = "" # Default value

# Schema for the QA endpoint request body
# Adjust fields based on what your QA endpoint actually expects
class QaRequest(BaseModel):
    trace: Optional[str] = None
    patch: str
    language: str = "python"
    source_files: Dict[str, str] = Field(default_factory=dict)
    patched_file_name: str = "N/A" # Assuming this is needed for context

# Schema for the QA endpoint response body
# Adjust fields based on what your QA endpoint actually returns
class QaResponse(BaseModel):
    llm_qa_result: str = "No LLM review provided."
    static_analysis_result: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict) # Dict of filename -> list of issues

# Add schemas for /doc and voice responses (transcribe, speak) if needed
# class DocRequest(...): ...
# class DocResponse(...): ...
# class TranscribeResponse(BaseModel):
#     transcript: str = ""
#     error: Optional[str] = None # Include error field for transcription

# class SpeakRequest(BaseModel): # Assuming speak takes text_command
#     text_command: str
# # Speak response is likely audio data, not a JSON schema
