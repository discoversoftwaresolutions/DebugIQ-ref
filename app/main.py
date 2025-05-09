# File: DebuIQ-backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Core DebugIQ Modules
from app.api import analyze
from app.api import qa
from app.api import doc
from app.api import config
from app.api import voice

# Voice Interaction (Bidirectional Audio)
from app.api.voice_interactive_router import router as voice_interactive_router

# Agent Routers
from app.api.autonomous_router import router as autonomous_router
from app.api.metrics_router import router as metrics_router
from app.api.issues_router import router as issues_router

# Initialize FastAPI app
app = FastAPI(title="DebugIQ API - GPT-4o & Gemini Powered")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ In production, replace with frontend domain(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Core Debugging Agents
app.include_router(analyze.router, prefix="/debugiq", tags=["Analysis"])
app.include_router(qa.router, prefix="/qa", tags=["Quality Assurance"])
app.include_router(doc.router, prefix="/doc", tags=["Documentation"])

# Voice Routers
app.include_router(voice.router, prefix="/voice", tags=["Voice Assistant"])
app.include_router(voice_interactive_router, prefix="/voice", tags=["Voice Interactive"])

# Platform Config API
app.include_router(config.config_router, prefix="/api", tags=["Configuration"])

# Autonomous Orchestration & Status
app.include_router(autonomous_router, prefix="/workflow", tags=["Autonomous Workflow"])

# Issue Management
app.include_router(issues_router, tags=["Issues"])

# Metrics/Analytics API
app.include_router(metrics_router, tags=["Metrics"])

# Root and health check endpoints
@app.get("/")
async def read_root():
    return {"message": "Welcome to the DebugIQ API"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "API is running"}
