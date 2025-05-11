# scripts/utils/ai_api_clients.py

import os
import openai
import google.generativeai as genai

# --- Environment Configuration ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in environment")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in environment")

# --- Model Configuration ---
OPENAI_MODEL = "gpt-4o"
GEMINI_MODEL = "models/gemini-pro"

# --- Configure Clients ---
openai.api_key = OPENAI_API_KEY
genai.configure(api_key=GEMINI_API_KEY)

# --- OpenAI GPT-4o Handler ---
def call_codex(prompt: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a senior AI debugging agent."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Codex Error] {str(e)}"

# --- Gemini Handler (Used for voice commands or fallback) ---
def call_gemini(prompt: str) -> str:
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[Gemini Error] {str(e)}"

# --- Main Routing Logic ---
def call_ai_agent(task_type: str, prompt: str) -> str:
    """
    Unified entrypoint for any DebugIQ AI agent task.
    """
    if task_type == "voice_command":
        return call_gemini(prompt)
    else:
        return call_codex(prompt)
