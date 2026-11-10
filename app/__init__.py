"""VibeDrop, a local YouTube to MP3 tool with a window."""

__version__ = "1.2.0"

# A yt-dlp updated from inside the app lives in the data folder. Put it in front
# of the bundled one before any module imports yt_dlp. The import is guarded so a
# broken update can never stop the app from starting.
try:
    from .updates import prefer_staged as _prefer_staged

    _prefer_staged()
except Exception:
    pass
