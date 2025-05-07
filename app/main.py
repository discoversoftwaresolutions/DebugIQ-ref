from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import analyze, qa, doc

app = FastAPI(title="DebugIQ API - GPT-4o Powered")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with front-end domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount GPT-4o micro-agents
app.include_router(analyze.router, prefix="/debugiq")
app.include_router(qa.router, prefix="/qa")
app.include_router(doc.router, prefix="/doc")
