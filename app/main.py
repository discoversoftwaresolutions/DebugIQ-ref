# Content for: /app/app/main.py (or your_project_root/main.py)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import all API routers
# Note: This assumes each imported module (analyze.py, qa.py, etc.)
# defines a variable named 'router' (or 'config_router' for config)
# at its top level.
from app.api import analyze, qa, doc, config, voice

# Import routers from the 'agents' package
# Note: This assumes app/api/agents/__init__.py makes these modules importable
# and that each module (autonomous_router.py, metrics_router.py, issues_router.py)
# defines a variable named 'router' at its top level.
from app.api.autonomous_router import router as autonomous_router
from app.api.metrics_router import router as metrics_router
from app.api.issues_router import router as issues_router


# Initialize FastAPI app
# This line defines the 'app' attribute that the server looks for
app = FastAPI(title="DebugIQ API - GPT-4o & Gemini Powered")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Consider restricting this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include all API routers
# Use the imported router objects directly (router or config_router)
app.include_router(analyze.router, prefix="/debugiq", tags=["Analysis"])
app.include_router(qa.router, prefix="/qa", tags=["Quality Assurance"])
app.include_router(doc.router, prefix="/doc", tags=["Documentation"])
app.include_router(voice.router, prefix="/voice", tags=["Voice Assistant"])
app.include_router(config.config_router, prefix="/api", tags=["Configuration"])

# Use the routers imported *as* specific names
app.include_router(autonomous_router, prefix="/workflow", tags=["Autonomous Workflow"])
app.include_router(metrics_router) # Assuming this router's paths don't need a prefix
app.include_router(issues_router) # Assuming this router's paths don't need a prefix


# Standard root and health check endpoints
@app.get("/")
async def read_root():
    return {"message": "Welcome to the DebugIQ API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# There should be NO code below this point that tries to write to files
# or modify the script itself.
