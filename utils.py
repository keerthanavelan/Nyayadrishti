import json
import os

# File paths for storing notes and reminders
NOTES_FILE = "notes.json"
REMINDERS_FILE = "reminders.json"

# ----------------------------
# Notes Functions
# ----------------------------
def load_notes():
    """Load lawyer notes from JSON file."""
    if os.path.exists(NOTES_FILE):
        try:
            with open(NOTES_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_notes(notes):
    """Save lawyer notes to JSON file."""
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f)

# ----------------------------
# Reminders Functions
# ----------------------------
def load_reminders():
    """Load lawyer reminders from JSON file."""
    if os.path.exists(REMINDERS_FILE):
        try:
            with open(REMINDERS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_reminders(reminders):
    """Save lawyer reminders to JSON file."""
    with open(REMINDERS_FILE, "w") as f:
        json.dump(reminders, f)