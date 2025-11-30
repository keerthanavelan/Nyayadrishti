import json
import uuid
from pathlib import Path
from typing import Optional

SESSIONS_FILE = Path(__file__).parent / "sessions.json"

def _load_sessions() -> dict:
    if SESSIONS_FILE.exists():
        try:
            with open(SESSIONS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_sessions(sessions: dict) -> None:
    try:
        SESSIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SESSIONS_FILE, "w") as f:
            json.dump(sessions, f, indent=2)
        print(f"[SESSIONS] _save_sessions: saved {len(sessions)} tokens to {SESSIONS_FILE}")
    except Exception as e:
        print(f"[SESSIONS] _save_sessions: ERROR saving to {SESSIONS_FILE}: {e}")


def create_token(username: str) -> str:
    """Create and store a session token for username, return token."""
    sessions = _load_sessions()
    token = uuid.uuid4().hex
    sessions[username.lower()] = token
    _save_sessions(sessions)
    print(f"[SESSIONS] create_token('{username}'): token created, sessions now: {list(sessions.keys())}")
    return token


def validate_token(username: str, token: Optional[str]) -> bool:
    """Return True if stored token for username matches provided token."""
    if not username or not token:
        return False
    sessions = _load_sessions()
    valid = sessions.get(username.lower()) == token
    print(f"[SESSIONS] validate_token('{username}'): valid={valid}, has_token={username.lower() in sessions}")
    return valid


def delete_token(username: str) -> None:
    """Delete stored token for username (logout)."""
    sessions = _load_sessions()
    was_present = username.lower() in sessions
    sessions.pop(username.lower(), None)
    _save_sessions(sessions)
    print(f"[SESSIONS] delete_token('{username}'): was_present={was_present}, remaining_sessions={list(sessions.keys())}")


def get_token(username: str) -> Optional[str]:
    sessions = _load_sessions()
    token = sessions.get(username.lower())
    print(f"[SESSIONS] get_token('{username}'): token_present={token is not None}")
    return token