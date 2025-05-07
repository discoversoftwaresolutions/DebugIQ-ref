import google.generativeai as genai
import base64
from typing import Tuple
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def transcribe_audio_bytes(audio_bytes: bytes, mime_type: str = "audio/wav") -> str:
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    response = model.generate_content(
        contents=[{
            "role": "user",
            "parts": [{"inline_data": {"mime_type": mime_type, "data": base64.b64encode(audio_bytes).decode()}}]
        }],
        generation_config={"temperature": 0.5}
    )
    return response.text

def synthesize_speech(text: str) -> Tuple[bytes, str]:
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    response = model.generate_content(
        contents=[{"role": "user", "parts": [{"text": f"Say this clearly and naturally: {text}"}]}],
        generation_config={"response_mime_type": "audio/wav"}
    )
    audio_part = next(p for p in response.parts if "inline_data" in p)
    audio_data = base64.b64decode(audio_part["inline_data"]["data"])
    mime_type = audio_part["inline_data"].get("mime_type", "audio/wav")
    return audio_data, mime_type
