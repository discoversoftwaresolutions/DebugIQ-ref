# Save a corrected and production-ready version of main.py for the DebugIQ backend

main_py_code = '''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from app.api import analyze, qa, doc, config, voice
from app.api.agents import (
    fix_memory_router,
    regression_monitor_router,
    rollback_or_deploy_router
)

# Instantiate FastAPI first
app = FastAPI(title="DebugIQ API - GPT-4o & Gemini Powered")

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agent routers
app.include_router(fix_memory_router.router, prefix="/agents", tags=["Fix Memory"])
app.include_router(regression_monitor_router.router, prefix="/agents", tags=["Regression Monitor"])
app.include_router(rollback_or_deploy_router.router, prefix="/agents", tags=["Deploy Manager"])

# Core functionality
app.include_router(analyze.router, prefix="/debugiq", tags=["Analysis"])
app.include_router(qa.router, prefix="/qa", tags=["Quality Assurance"])
app.include_router(doc.router, prefix="/doc", tags=["Documentation"])
app.include_router(voice.router, prefix="/voice", tags=["Voice Assistant"])
app.include_router(config.config_router, prefix="/api", tags=["Configuration"])

# Health and root
@app.get("/")
async def read_root():
    return {"message": "Welcome to the DebugIQ API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
'''.strip()

main_path = Path("/mnt/data/DebugIQ-backend/app/main.py")
main_path.parent.mkdir(parents=True, exist_ok=True)
main_path.write_text(main_py_code + "\n")

main_path
