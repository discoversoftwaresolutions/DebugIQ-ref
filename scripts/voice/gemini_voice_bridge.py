import os
import tempfile
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
GEMINI_MODEL = "models/gemini-1.5-pro-latest"

def transcribe_and_respond_from_audio(audio_bytes: bytes) -> str:
    try:
        session = genai.StreamingVoiceChatSession(model=GEMINI_MODEL)
        session.send_audio_chunk(audio_bytes)

        full_response = ""
        for chunk in session:
            if chunk.text:
                full_response += chunk.text
        return full_response.strip()
    except Exception as e:
        return f"[Gemini voice error] {e}"
