"""A YouTube link in, an MP3 out. The whole pipeline lives here.

The download runs with yt-dlp exactly as the old script did, except that progress
is reported to a callback instead of printed, so the window can show it.
"""

from __future__ import annotations

import os
import re
import shutil
import sys
import time
from pathlib import Path

from .i18n import t

SUPPORTED = re.compile(
    r"^https?://(?:www\.|m\.|music\.)?"
    r"(?:youtube\.com/(?:watch\?|shorts/|live/|clip/)|youtu\.be/)",
    re.IGNORECASE,
)

# What the user actually gets to read when something goes wrong. The keys live in
# app/i18n.py, so the sentence follows the language chosen in Settings.
_HINTS = (
    ("sign in to confirm", "download.sign_in"),
    ("video is unavailable", "download.unavailable"),
    ("video unavailable", "download.unavailable"),
    ("private video", "download.private"),
    ("age-restricted", "download.age"),
    ("members-only", "download.members"),
    ("not available in your country", "download.country"),
    ("unsupported url", "download.unsupported"),
    ("http error 403", "download.403"),
    ("http error 429", "download.429"),
    ("timed out", "download.timeout"),
    ("unable to download", "download.unable"),
)


def normalize_url(raw: str) -> str:
    url = (raw or "").strip()
    if url and not re.match(r"^https?://", url, re.IGNORECASE):
        url = "https://" + url.lstrip("/")
    return url


def is_supported(url: str) -> bool:
    return bool(SUPPORTED.match(normalize_url(url)))


def ffmpeg_location() -> str | None:
    """Bundled first, then PATH, then imageio-ffmpeg if the packager added it."""
    exe = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    roots = []
    if getattr(sys, "_MEIPASS", None):
        roots.append(Path(sys._MEIPASS))
    if getattr(sys, "frozen", False):
        roots.append(Path(sys.executable).parent)
    roots.append(Path(__file__).resolve().parent.parent)
    roots.append(Path.cwd())

    candidates = [os.environ.get("MUSIC_EXTRACTOR_FFMPEG")]
    candidates += [root / "bin" / exe for root in roots]
    candidates += [root / exe for root in roots]
    candidates.append(shutil.which("ffmpeg"))

    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(candidate)

    try:  # optional, only if a build ever bundles it this way
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def clean_error(exc: Exception) -> str:
    """One readable line instead of yt-dlp's stack of ERROR: noise."""
    text = re.sub(r"^ERROR:\s*", "", str(exc).strip())
    first = text.splitlines()[0] if text else exc.__class__.__name__
    first = re.sub(r"^\[[^\]]+\]\s*[^:]*:\s*", "", first)
    lowered = first.lower()
    for needle, key in _HINTS:
        if needle in lowered:
            return t(key)
    return first[:280] or t("download.unknown_error")


def download(
    url: str,
    *,
    outdir: str | os.PathLike,
    bitrate: str = "192",
    on_progress=None,
    cookies: str | os.PathLike | None = None,
) -> dict:
    """Download the audio, convert it to MP3, return where it landed."""
    # Imported here — not at module load — so an updated yt-dlp staged at runtime
    # is the one that runs on the next download.
    import yt_dlp

    folder = Path(outdir).expanduser()
    folder.mkdir(parents=True, exist_ok=True)

    started = time.time()
    ffmpeg = ffmpeg_location()
    if not ffmpeg:
        raise RuntimeError(t("download.ffmpeg_missing"))

    def report(stage: str, percent: float | None):
        if on_progress is None:
            return
        try:
            on_progress(stage, None if percent is None else max(0.0, min(100.0, percent)))
        except Exception:
            pass  # a UI that went away must never kill the download

    def on_download(chunk: dict):
        if chunk.get("status") == "downloading":
            total = chunk.get("total_bytes") or chunk.get("total_bytes_estimate")
            done = chunk.get("downloaded_bytes") or 0
            report("downloading", (done / total * 100) if total else None)
        elif chunk.get("status") == "finished":
            report("converting", None)

    def on_postprocess(chunk: dict):
        if chunk.get("status") in ("started", "processing", "finished"):
            report("converting", None)

    options = {
        "format": "bestaudio/best",
        "outtmpl": str(folder / "%(title)s.%(ext)s"),
        "noplaylist": True,
        "windowsfilenames": True,
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "retries": 3,
        "fragment_retries": 3,
        "socket_timeout": 30,
        "ffmpeg_location": ffmpeg,
        "progress_hooks": [on_download],
        "postprocessor_hooks": [on_postprocess],
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": str(bitrate),
            }
        ],
    }
    if cookies and Path(cookies).is_file():
        options["cookiefile"] = str(cookies)

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(normalize_url(url), download=True)

    if info.get("_type") == "playlist":  # defensive: noplaylist should prevent this
        entries = [entry for entry in (info.get("entries") or []) if entry]
        if entries:
            info = entries[0]

    filepath = _final_path(info) or _newest_mp3(folder, started)
    if not filepath:
        raise RuntimeError(t("download.no_mp3"))

    return {
        "title": info.get("title") or Path(filepath).stem,
        "duration": int(info.get("duration") or 0),
        "file": str(Path(filepath)),
        "size_mb": Path(filepath).stat().st_size / (1024 * 1024),
    }


def _final_path(info: dict) -> str | None:
    """Where yt-dlp says the post-processed file is, if it still exists."""
    for item in info.get("requested_downloads") or []:
        candidate = item.get("filepath") or item.get("_filename")
        if not candidate:
            continue
        path = Path(candidate)
        if path.suffix.lower() != ".mp3":
            converted = path.with_suffix(".mp3")
            if converted.is_file():
                return str(converted)
        if path.is_file():
            return str(path)
    return None


def _newest_mp3(folder: Path, since: float) -> str | None:
    files = [p for p in folder.glob("*.mp3") if p.stat().st_mtime >= since - 2]
    if not files:
        return None
    return str(max(files, key=lambda p: p.stat().st_mtime))
