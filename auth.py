#Stores passwords in a JSON file for cross-device synchronization.

import json
import hashlib
from pathlib import Path
from typing import Dict, Optional

PASSWORD_FILE = Path(__file__).parent / "passwords.json"

def _hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def _load_passwords() -> Dict:
    """Load passwords from JSON file."""
    if PASSWORD_FILE.exists():
        try:
            with open(PASSWORD_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def _save_passwords(passwords: Dict) -> None:
    """Save passwords to JSON file."""
    PASSWORD_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PASSWORD_FILE, 'w') as f:
        json.dump(passwords, f, indent=2)

def user_exists(name: str) -> bool:
    """Check if a user has set a custom password."""
    passwords = _load_passwords()
    return name.lower() in passwords

def is_first_login(name: str) -> bool:
    """Check if this is a user's first login."""
    return not user_exists(name)

def verify_password(name: str, password: str, merged_df=None) -> bool:
    """
    Verify if password is correct.
    On first login, accepts default password (first 4 letters + "01").
    After first login, requires custom password.
    """
    name_lower = name.lower()
    passwords = _load_passwords()
    
    # First login: use default password
    if name_lower not in passwords:
        default_password = name[:4].upper() + "01"
        return password == default_password
    
    # Subsequent logins: use custom password (hashed)
    return passwords[name_lower] == _hash_password(password)

def set_password(name: str, password: str) -> bool:
    """
    Set or update a user's password.
    Stores hashed password in JSON file.
    """
    try:
        passwords = _load_passwords()
        passwords[name.lower()] = _hash_password(password)
        _save_passwords(passwords)
        return True
    except Exception as e:
        print(f"Error saving password: {e}")
        return False

def get_default_password(name: str) -> str:
    """Get the default password for a user on first login."""
    return name[:4].upper() + "01"
