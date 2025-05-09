from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Rename routers at import for clarity
from app.api.issues_router import router as issues_router
from app.api.metrics_router import router as metrics_router
from app.api.autonomous_router import router as autonomous_router

from app.api import analyze, qa, doc, config, voice
from app.api.agents import (
    fix_memory_router,
    regression_monitor_router,
    
)

app = FastAPI(title="DebugIQ API - GPT-4o & Gemini Powered")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(issues_router)
app.include_router(metrics_router)
app.include_router(autonomous_router)

app.include_router(fix_memory_router.router, prefix="/agents", tags=["Fix Memory"])
app.include_router(regression_monitor_router.router, prefix="/agents", tags=["Regression Monitor"])
app.include_router(analyze.router, prefix="/debugiq", tags=["Analysis"])
app.include_router(qa.router, prefix="/qa", tags=["Quality Assurance"])
app.include_router(doc.router, prefix="/doc", tags=["Documentation"])
app.include_router(voice.router, prefix="/voice", tags=["Voice Assistant"])
app.include_router(config.config_router, prefix="/api", tags=["Configuration"])
app.include_router(autonomous_router)@app.get("/")

async def read_root():
    return {"message": "Welcome to the DebugIQ API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
