def map_command_to_action(command: str) -> str:
    if "analyze" in command.lower(): return "analyze"
    elif "qa" in command.lower(): return "qa"
    elif "document" in command.lower(): return "doc"
    return "unknown"
