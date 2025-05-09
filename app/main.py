# Content for: DebuIQ-backend/app/main.py (or your_project_root/app/main.py)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import all API routers
# Note: This assumes each imported module defines a variable named 'router'
# (or 'config_router' for config) at its top level.
from app.api import analyze
from app.api import qa
from app.api import doc
from app.api import config # Assumed to have config_router
from app.api import voice # Assumed to have voice.router
# Added import for voice_interactive, assuming it exports router
from app.api import voice_interactive # Assumed to have voice_interactive.router

# Import routers from specific files if they are not in __init__.py or named differently
# Note: Adjusted imports based on common structure and your use below
from app.api.autonomous_router import router as autonomous_router
from app.api.metrics_router import router as metrics_router
from app.api.issues_router import router as issues_router # Likely contains /issues/inbox


# Initialize FastAPI app
# This line defines the 'app' attribute that the server looks for
app = FastAPI(title="DebugIQ API - GPT-4o & Gemini Powered")

# CORS configuration
# WARNING: allow_origins=["*"] is insecure for production.
# Change "*" to the specific URL(s) where your Streamlit app is hosted.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # <<< CHANGE THIS FOR PRODUCTION
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include all API routers
# Use the imported router objects directly
app.include_router(analyze.router, prefix="/debugiq", tags=["Analysis"])
app.include_router(qa.router, prefix="/qa", tags=["Quality Assurance"])
app.include_router(doc.router, prefix="/doc", tags=["Documentation"])

# --- Voice Routers ---
# Potential Conflict: Including two routers with the same prefix '/voice'.
# Review app/api/voice.py and app/api/voice_interactive.py to consolidate or use different prefixes/tags if needed.
app.include_router(voice.router, prefix="/voice", tags=["Voice Assistant"])
app.include_router(voice_interactive.router, prefix="/voice", tags=["Voice Interactive"]) # Corrected import and added tags

app.include_router(config.config_router, prefix="/api", tags=["Configuration"])

# --- Workflow / Issues Routers ---
# The /workflow/status 404 error means the 'autonomous_router'
# likely does not have a GET /status path defined within app/api/autonomous_router.py
app.include_router(autonomous_router, prefix="/workflow", tags=["Autonomous Workflow"])

# The 500 error for /issues/inbox likely happens in code called by the 'issues_router'
# Check app/api/issues_router.py and modules it imports (like scripts.platform_data_api)
app.include_router(issues_router, tags=["Issues"]) # Assuming /issues paths, no prefix needed

# Assuming metrics_router paths also don't need a prefix
app.include_router(metrics_router, tags=["Metrics"])


# Standard root and health check endpoints
@app.get("/")
async def read_root():
    return {"message": "Welcome to the DebugIQ API"}

@app.get("/health")
async def health_check():
    # Add more robust health checks here if needed (e.g., database connection)
    return {"status": "ok", "message": "API is running"}


# There should be NO code below this point that tries to write to files
# or modify the script itself
