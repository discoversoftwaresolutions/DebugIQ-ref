from fastapi import APIRouter, Request
from app.schemas import ApiEndpoints


config_router = APIRouter()

@config_router.get("/config", response_model=ApiEndpoints, tags=["Configuration"])
async def get_api_endpoints(request: Request):
    base_url = str(request.base_url).rstrip('/')
    return ApiEndpoints(
        analyze=f"{base_url}/debugiq/analyze",
        qa=f"{base_url}/qa/",
        doc=f"{base_url}/doc/",
        voice_transcribe=f"{base_url}/voice/transcribe",
        voice_command=f"{base_url}/voice/command",
        voice_speak=f"{base_url}/voice/speak",
        model="gpt-4o",
        voice_provider="gemini",
        debug=True
    )
# Define the API router for configuration endpoints
config_router = APIRouter()

@config_router.get("/config", response_model=ApiEndpoints, tags=["Configuration"])
async def get_api_endpoints(request: Request):
    """
    Returns the dynamically constructed URLs for the backend API endpoints.
    This endpoint is called by the frontend on startup to get backend URLs.
    """
    # Construct the base URL from the incoming request (scheme + host)
    base_url = str(request.base_url).rstrip('/')

    # Return the ApiEndpoints model with the correct full URLs.
    # These paths must match how you include routers in main.py.
    return ApiEndpoints(
        analyze=f"{base_url}/debugiq/analyze",
        qa=f"{base_url}/qa/", # Assuming /qa/ is the base for QA endpoints
        doc=f"{base_url}/doc/", # Assuming /doc/ is the base for Doc endpoints
        voice_transcribe=f"{base_url}/voice/transcribe", # Assuming /voice is the prefix
        voice_command=f"{base_url}/voice/command",
        voice_speak=f"{base_url}/voice/speak",
        # Add other endpoints from your ApiEndpoints schema here
        # Example if QA had a specific endpoint like /qa/analyze-patch:
        # qa_analyze_patch=f"{base_url}/qa/analyze-patch"
    )

# Remember to also have your app/schemas.py file with the ApiEndpoints BaseModel:
# # DebugIQ-backend/app/schemas.py
# from pydantic import BaseModel
#
# class ApiEndpoints(BaseModel):
#     analyze: str
#     qa: str
#     doc: str
#     voice_transcribe: str
#     voice_command: str
#     voice_speak: str
#     # Add other endpoint fields here if needed to match the ApiEndpoints model
#
# # Define other schemas like AnalyzeRequest, AnalyzeResponse, CommandRequest here
# # ...
