# scripts/utils/ai_api_client.py

import os
import openai
import google.generativeai as genai

# --- OpenAI Setup ---
openai.api_key = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o"

# --- Gemini Setup (only used for voice or fallback) ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
GEMINI_MODEL = "models/gemini-pro"

def call_codex(prompt: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a senior debugging agent."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[OpenAI error] {str(e)}"

def call_gemini(prompt: str) -> str:
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[Gemini error] {str(e)}"

def call_ai_agent(task_type: str, prompt: str) -> str:
    if task_type == "voice_command":
        return call_gemini(prompt)
    return call_codex(prompt)
