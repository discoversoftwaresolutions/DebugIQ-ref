from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import analyze # Assumes analyze.py exists in app/api
from app.api import qa      # Assumes qa.py exists in app/api
from app.api import doc     # Assumes doc.py exists in app/api
from app.api import config  # Assumes config.py exists in app/api for API endpoint configuration
from app.api import voice   # Assumes voice.py exists in app/api for voice features

app = FastAPI(title="DebugIQ API - GPT-4o & Gemini Powered")

# Configure CORS to allow front-end access
# IMPORTANT: Replace allow_origins=["*"] with your front-end domain(s) in production!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins during development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# --- Include Routers for Different API Sections ---

# Core Debugging and Analysis agent routes (e.g., /debugiq/analyze)
# This is where the primary trace/code analysis using GPT-4o happens.
app.include_router(analyze.router, prefix="/debugiq", tags=["Analysis"])

# Quality Assurance agent routes (e.g., /qa/analyze-patch)
# Handles LLM review and static analysis of code/patches.
app.include_router(qa.router, prefix="/qa", tags=["Quality Assurance"])

# Documentation agent routes (e.g., /doc/generate)
# Focuses on generating or summarizing documentation.
app.include_router(doc.router, prefix="/doc", tags=["Documentation"])

# Voice Assistant routes (e.g., /voice/transcribe, /voice/command, /voice/speak)
# Interfaces with Gemini for voice-based interactions.
app.include_router(voice.router, prefix="/voice", tags=["Voice Assistant"])

# API Configuration routes (e.g., /api/config)
# Provides dynamic configuration information, like endpoint URLs, to the front-end.
app.include_router(config.config_router, prefix="/api", tags=["Configuration"])

# Optional: Root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the DebugIQ API"}

# Optional: Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}
