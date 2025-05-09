from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse
from scripts.voice.gemini_voice_bridge import transcribe_and_respond_from_audio
from scripts.utils.tts_google import synthesize_speech_to_bytes  # Optional TTS engine
import io

router = APIRouter()

@router.post("/voice/interactive", tags=["Voice Assistant"])
async def voice_interactive(file: UploadFile = File(...)):
    """
    Accepts raw audio input, sends to Gemini for transcription and agent response,
    and returns a synthesized spoken reply using TTS as audio/wav.
    """
    audio_data = await file.read()

    # Transcribe audio and generate response using Gemini
    gemini_reply_text = transcribe_and_respond_from_audio(audio_data)

    # Convert Gemini's text reply into speech audio
    tts_audio_bytes = synthesize_speech_to_bytes(gemini_reply_text)

    return StreamingResponse(io.BytesIO(tts_audio_bytes), media_type="audio/wav")
