import json
import os
from datetime import datetime

MEMORY_FILE = os.getenv("FIX_MEMORY_FILE", "fix_memory.json")

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def record_fix(issue_id, trace, patch_diff, validation_feedback):
    """Append a record of the fix to memory."""
    memory = load_memory()
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "issue_id": issue_id,
        "trace": trace,
        "patch_diff": patch_diff,
        "validation_feedback": validation_feedback
    }
    memory.append(entry)
    save_memory(memory)
    print(f"Recorded fix for {issue_id} into memory.")
