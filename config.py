"""
Configuration and constants for the Keybind Manager application.
"""
import os
import sys

# Application constants
APP_TITLE = "✨ TEXT MACRO KEYBINDER BY MIFUZI"
APP_TITLE_FALLBACK = "TEXT MACRO KEYBINDER BY MIFUZI"
WINDOW_SIZE = "1000x750"
MIN_WINDOW_SIZE = (1000, 700)

# Available hotkeys for dropdown
AVAILABLE_HOTKEYS = [
    # Function Keys
    "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
    # Numpad Numbers
    "numpad 0", "numpad 1", "numpad 2", "numpad 3", "numpad 4",
    "numpad 5", "numpad 6", "numpad 7", "numpad 8", "numpad 9",
    # Numpad Operators
    "numpad +", "numpad -", "numpad *", "numpad /", "numpad enter", "numpad .",
    # Special Characters
    ".", ",", ";", ":", "'", '"', "[", "]", "{", "}", "\\", "|", "/", "?",
    # Modifier Combinations (Function Keys)
    "ctrl+F1", "ctrl+F2", "ctrl+F3", "ctrl+F4", "ctrl+F5",
    "shift+F1", "shift+F2", "shift+F3", "shift+F4", "shift+F5",
    "alt+F1", "alt+F2", "alt+F3", "alt+F4", "alt+F5",
    # Modifier Combinations (Special Keys)
    "ctrl+.", "ctrl+,", "ctrl+;", "ctrl+:", "ctrl+/",
    "shift+.", "shift+,", "shift+;", "shift+:", "shift+/",
    "alt+.", "alt+,", "alt+;", "alt+:", "alt+/",
    # Common Modifier Combinations
    "ctrl+a", "ctrl+b", "ctrl+c", "ctrl+d", "ctrl+e", "ctrl+f", "ctrl+g", "ctrl+h",
    "ctrl+i", "ctrl+j", "ctrl+k", "ctrl+l", "ctrl+m", "ctrl+n", "ctrl+o", "ctrl+p",
    "ctrl+q", "ctrl+r", "ctrl+s", "ctrl+t", "ctrl+u", "ctrl+v", "ctrl+w", "ctrl+x",
    "ctrl+y", "ctrl+z",
    "shift+a", "shift+b", "shift+c", "shift+d", "shift+e", "shift+f", "shift+g",
    "alt+a", "alt+b", "alt+c", "alt+d", "alt+e", "alt+f", "alt+g",
]

# Color scheme (glassmorphism style)
COLORS = {
    "bg_main": "#0a0a0f",
    "bg_sidebar": "#1a1a2e",
    "bg_header": "#16213e",
    "bg_card": "#16213e",
    "bg_input": "#0f3460",
    "bg_hover": "#0f3460",
    "text_primary": "#ffffff",
    "text_secondary": "#b8b8d1",
    "text_hint": "#6c6c8a",
    "accent_teal": "#00d4aa",
    "accent_teal_dark": "#00b894",
    "accent_orange": "#ffa726",
    "accent_orange_dark": "#fb8c00",
    "accent_red": "#ff6b6b",
    "accent_red_dark": "#ee5a6f",
}

# Typing delays (in seconds)
TYPING_DELAY_INITIAL = 0.05
TYPING_DELAY_PER_CHAR = 0.03
TYPING_DELAY_BEFORE_ENTER = 0.05


def get_config_path():
    """Return a stable path for keybinds.json.
    Prefer a *portable* keybinds.json next to the running script/executable.
    If that folder is not writable, fallback to Documents (NOT Roaming).
    """
    # Portable: directory of the running script/executable
    try:
        base_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
    except Exception:
        base_dir = os.getcwd()

    portable_path = os.path.join(base_dir, "keybinds.json")
    if _can_write_file(portable_path):
        return portable_path

    # Fallback: Documents\SAMP_Keybind\keybinds.json
    try:
        home = os.path.expanduser("~")
        documents = os.path.join(home, "Documents")
        root_dir = documents if os.path.isdir(documents) else home
        return os.path.join(root_dir, "SAMP_Keybind", "keybinds.json")
    except Exception:
        return os.path.join(os.getcwd(), "keybinds.json")


def get_legacy_config_path():
    """Old location (Roaming). We only use this to migrate existing users."""
    try:
        appdata = os.getenv("APPDATA")
        if not appdata:
            return None
        return os.path.join(appdata, "SAMP_Keybind", "keybinds.json")
    except Exception:
        return None


def _can_write_file(path):
    """Best-effort check if we can create/append a file at `path`."""
    try:
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "a", encoding="utf-8"):
            pass
        return True
    except Exception:
        return False

