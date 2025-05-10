import os
import openai
import google.generativeai as genai
from scripts.utils.logger import logger

# --- OpenAI Setup (Codex/GPT-4o) ---
openai.api_key = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o"

# --- Gemini Setup (Voice Command Only) ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
GEMINI_MODEL = "models/gemini-pro"

# --- GPT-4o handler (default for all text-based agents) ---
def call_codex(prompt):
    try:
        logger.info("Calling GPT-4o agent...")
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a senior debugging agent."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        result = response.choices[0].message.content.strip()
        logger.info("GPT-4o response received.")
        return result
    except Exception as e:
        logger.error(f"GPT-4o error: {e}")
        return f"[Codex error] {str(e)}"

# --- Gemini handler (only for voice commands) ---
def call_gemini(prompt):
    try:
        logger.info("Calling Gemini voice model...")
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        result = response.text.strip()
        logger.info("Gemini response received.")
        return result
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return f"[Gemini error] {str(e)}"

# --- Main interface ---
def call_ai_agent(task_type: str, prompt: str):
    logger.info(f"Dispatching task to agent (type={task_type})")
    if task_type == "voice_command":
        return call_gemini(prompt)
    else:
        return call_codex(prompt)
