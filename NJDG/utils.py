import json
import os

# File paths
NOTES_FILE = "notes.json"
REMINDERS_FILE = "reminders.json"
JUDGE_PASSWORD_FILE = "judge_passwords.json"
LAWYER_PASSWORD_FILE = "lawyer_passwords.json"

# ----------------------------
# JSON Helpers
# ----------------------------
def _load_json(path):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def _save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# ----------------------------
# Lawyer Password Functions
# ----------------------------
def load_lawyer_passwords():
    return _load_json(LAWYER_PASSWORD_FILE)

def save_lawyer_passwords(passwords):
    _save_json(LAWYER_PASSWORD_FILE, passwords)

def register_lawyer(lawyer_name, password):
    passwords = load_lawyer_passwords()
    passwords[lawyer_name.lower()] = password
    save_lawyer_passwords(passwords)

def validate_lawyer_login(lawyer_name, password):
    passwords = load_lawyer_passwords()
    return passwords.get(lawyer_name.lower()) == password

def reset_lawyer_password(lawyer_name, new_password):
    passwords = load_lawyer_passwords()
    if lawyer_name.lower() in passwords:
        passwords[lawyer_name.lower()] = new_password
        save_lawyer_passwords(passwords)
        return True
    return False

# ----------------------------
# Notes Functions
# ----------------------------
def load_notes():
    return _load_json(NOTES_FILE)

def save_notes(notes):
    _save_json(NOTES_FILE, notes)

# ----------------------------
# Reminders Functions
# ----------------------------
def load_reminders():
    return _load_json(REMINDERS_FILE)

def save_reminders(reminders):
    _save_json(REMINDERS_FILE, reminders)

# ----------------------------
# Judge Password Functions
# ----------------------------
def load_passwords():
    return _load_json(JUDGE_PASSWORD_FILE)

def save_passwords(passwords):
    _save_json(JUDGE_PASSWORD_FILE, passwords)

def register_judge(judge_name, password):
    passwords = load_passwords()
    passwords[judge_name] = password
    save_passwords(passwords)

def validate_login(judge_name, password):
    return load_passwords().get(judge_name) == password