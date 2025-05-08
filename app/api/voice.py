from fastapi import APIRouter, UploadFile, File # <--- Added UploadFile, File here
from pydantic import BaseModel
from app.utils.gpt4o_client import run_gpt4o_chat

import tempfile
import speech_recognition as sr
import pyttsx3
from fastapi.responses import StreamingResponse
import os # Added os for file path join if needed, and cleanup

router = APIRouter()

@router.post("/transcribe") # <--- Changed path from "/voice/transcribe" to "/transcribe"
def transcribe_voice(file: UploadFile = File(...)):
    """
    Receives an audio file, transcribes it using speech_recognition,
    and returns the text transcript.
    """
    recognizer = sr.Recognizer()
    # Use tempfile safely and ensure cleanup
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
        temp.write(file.file.read())
        temp_file_path = temp.name

    try:
        with sr.AudioFile(temp_file_path) as source:
            audio_data = recognizer.record(source)
            # Using recognize_google - requires internet access
            text = recognizer.recognize_google(audio_data)
            return {"transcript": text}
    except sr.UnknownValueError:
        return {"transcript": "", "error": "Speech Recognition could not understand audio"}
    except sr.RequestError as e:
        return {"transcript": "", "error": f"Could not request results from Google Speech Recognition service; {e}"}
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


class CommandRequest(BaseModel):
    text_command: str

@router.post("/command") # <--- Changed path from "/voice/command" to "/command"
def handle_command(cmd: CommandRequest):
    """
    Receives a text command and processes it using GPT-4o.
    Returns a text response to be spoken.
    """
    # Note: This uses GPT-4o for command processing, aligns with analyze/qa logic
    # If Gemini's language understanding is preferred for voice commands,
    # this would call a different utility function.
    response = run_gpt4o_chat("You are a voice assistant in DebugIQ.", cmd.text_command)
    return {"spoken_text": response}

# Using a fixed filename like "output.wav" is problematic for
# concurrent requests on a web server as multiple requests
# might try to write to or read from the same file simultaneously.
# A better approach is to generate audio data in memory or use a
# more robust method for temporary file handling per request.
@router.post("/speak") # <--- Changed path from "/voice/speak" to "/speak"
def synthesize_voice(cmd: CommandRequest):
    """
    Receives text and synthesizes speech using pyttsx3.
    Returns audio data as a WAV file stream.
    """
    # Using pyttsx3 - note potential concurrency issues with file handling
    # and that this uses a local TTS engine, not Gemini TTS as discussed
    engine = pyttsx3.init()

    # Use a temporary file for this request to avoid concurrency issues
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
        temp_output_path = temp.name

    try:
        # pyttsx3 requires a file path to save the audio
        engine.save_to_file(cmd.text_command, temp_output_path)
        engine.runAndWait() # Blocks until synthesis is complete

        # Stream the content of the temporary file
        return StreamingResponse(open(temp_output_path, "rb"), media_type="audio/wav")
    except Exception as e:
        # Basic error handling
        print(f"Error during text-to-speech synthesis: {e}")
        # Return an error response (consider a more structured error response)
        return {"error": "Failed to synthesize speech"}
    finally:
        # Clean up the temporary file after streaming
        if os.path.exists(temp_output_path):
             # Need to ensure the file is closed before deleting in some scenarios,
             # especially in async contexts or if the file object isn't closed
             # by StreamingResponse automatically. For robustness in production,
             # consider more advanced temp file management or async handlers.
             try:
                 os.remove(temp_output_path)
             except OSError as e:
                 print(f"Error removing temporary file {temp_output_path}: {e}")


# Note on Gemini Integration:
# The current implementation uses speech_recognition and pyttsx3.
# To integrate with Gemini's voice capabilities (STT and TTS) as planned,
# you would replace the logic within the /transcribe and /speak endpoints
# to call your Gemini client utility functions instead of these libraries.
# Example:
# from app.utils.gemini_client import transcribe_audio_with_gemini, synthesize_speech_with_gemini
#
# @router.post("/transcribe")
# async def transcribe_voice_gemini(file: UploadFile = File(...)):
#     audio_bytes = await file.read() # Read file asynchronously
#     transcript = await transcribe_audio_with_gemini(audio_bytes)
#     return {"transcript": transcript}
#
# @router.post("/speak")
# async def synthesize_voice_gemini(cmd: CommandRequest):
#      audio_bytes = await synthesize_speech_with_gemini(cmd.text_command)
#      # Stream audio bytes from memory or a temporary location
#      return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/wav") # Requires 'import io'
