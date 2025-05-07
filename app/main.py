from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import analyze, qa

app = FastAPI(title="DebugIQ API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict to front-end domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/debugiq")
app.include_router(qa.router, prefix="/qa")
