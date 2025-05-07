@router.post("/voice/command")
def process_voice_command(input: VoiceCommandRequest):
    action = map_command_to_action(input.text_command)
    return VoiceCommandResponse(
        spoken_text=...,  # In future: Gemini TTS
        action_triggered=action
    )
