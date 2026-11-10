"""Where the settings and the history live, and how they are read back.

Everything personal sits in the user's own profile, never next to the code:
%APPDATA%\\VibeDrop on Windows, ~/.config on Linux, Library on macOS.
MUSIC_EXTRACTOR_HOME overrides the folder (used by the tests and by Termux).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

APP_NAME = "VibeDrop"
DEFAULT_BITRATE = "192"
BITRATES = ("128", "192", "256", "320")
LANGUAGES = ("en", "it", "es")
DEFAULT_LANGUAGE = "en"
THEMES = ("dark", "light", "system")
DEFAULT_THEME = "dark"
DEFAULT_DOWNLOAD_DETAILS = "🎵 {title}\n⏱ Duration: {duration}\n📦 Size: {size}"


def data_dir() -> Path:
    """The one folder the app writes to."""
    override = os.environ.get("MUSIC_EXTRACTOR_HOME")
    if override:
        base = Path(override).expanduser()
    elif sys.platform == "win32":
        roaming = os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming"
        base = Path(roaming) / APP_NAME
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / APP_NAME
    else:
        config_home = os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
        base = Path(config_home) / APP_NAME
    base.mkdir(parents=True, exist_ok=True)
    return base


def default_output_dir() -> Path:
    """Music/VibeDrop when the Music folder exists, else the home folder."""
    music = Path.home() / "Music"
    if not music.is_dir():
        music = Path.home()
    return music / APP_NAME


def settings_path() -> Path:
    return data_dir() / "settings.json"


def state_path() -> Path:
    return data_dir() / "state.json"


def cookies_path() -> Path | None:
    """An optional cookies.txt in the data folder, for videos that need a sign-in."""
    candidate = data_dir() / "cookies.txt"
    return candidate if candidate.is_file() else None


def _defaults() -> dict:
    return {
        "token": "",
        "chat_id": "",
        "bitrate": DEFAULT_BITRATE,
        "output_dir": str(default_output_dir()),
        # the window, and the few sentences the server says back to it
        "language": DEFAULT_LANGUAGE,
        "theme": DEFAULT_THEME,
        "download_details": DEFAULT_DOWNLOAD_DETAILS,
        # kept for compatibility with existing settings files
        "seen_guide": False,
    }


def load_settings() -> dict:
    data = _defaults()
    path = settings_path()
    if path.is_file():
        try:
            stored = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            stored = {}
        if isinstance(stored, dict):
            data.update({key: value for key, value in stored.items() if key in data})

    # The environment wins, for anyone who would rather keep the token out of a file.
    if os.environ.get("TELEGRAM_TOKEN"):
        data["token"] = os.environ["TELEGRAM_TOKEN"]
    if os.environ.get("TELEGRAM_CHAT_ID"):
        data["chat_id"] = os.environ["TELEGRAM_CHAT_ID"]

    if data["bitrate"] not in BITRATES:
        data["bitrate"] = DEFAULT_BITRATE
    if data["language"] not in LANGUAGES:
        data["language"] = DEFAULT_LANGUAGE
    if data["theme"] not in THEMES:
        data["theme"] = DEFAULT_THEME
    if not str(data["output_dir"]).strip():
        data["output_dir"] = str(default_output_dir())
    if not str(data["download_details"]).strip():
        data["download_details"] = DEFAULT_DOWNLOAD_DETAILS
    return data


def save_settings(patch: dict) -> dict:
    current = load_settings()
    for key, value in (patch or {}).items():
        if key == "seen_guide":
            current[key] = bool(value)
        elif key == "bitrate":
            value = str(value)
            current[key] = value if value in BITRATES else current[key]
        elif key == "language":
            value = str(value)
            if value in LANGUAGES:
                current[key] = value
        elif key == "theme":
            value = str(value)
            if value in THEMES:
                current[key] = value
        elif key in ("token", "chat_id", "output_dir", "download_details"):
            current[key] = str(value or "").strip()
    if not current["output_dir"]:
        current["output_dir"] = str(default_output_dir())
    write_json(settings_path(), current)
    return current


def write_json(path: Path, payload) -> None:
    """Write through a temp file so a crash never leaves half a JSON file."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def read_json(path: Path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return fallback
