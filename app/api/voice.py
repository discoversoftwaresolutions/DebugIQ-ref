from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from app.utils.gpt4o_client import run_gpt4o_chat

import tempfile
import speech_recognition as sr
import pyttsx3
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.post("/voice/transcribe")
def transcribe_voice(file: UploadFile = File(...)):
    recognizer = sr.Recognizer()
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(file.file.read())
        temp.flush()
        with sr.AudioFile(temp.name) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return {"transcript": text}

class CommandRequest(BaseModel):
    text_command: str

@router.post("/voice/command")
def handle_command(cmd: CommandRequest):
    response = run_gpt4o_chat("You are a voice assistant in DebugIQ.", cmd.text_command)
    return {"spoken_text": response}

@router.post("/voice/speak")
def synthesize_voice(cmd: CommandRequest):
    engine = pyttsx3.init()
    engine.save_to_file(cmd.text_command, "output.wav")
    engine.runAndWait()
    return StreamingResponse(open("output.wav", "rb"), media_type="audio/wav")
