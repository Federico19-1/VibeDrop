"""Keeping yt-dlp fresh without asking anyone to open a terminal.

YouTube changes its pages constantly; an old yt-dlp is the most common reason a
download that worked yesterday stops working today. The app asks PyPI in the
background, shows a quiet notice when there is something newer, and — when the
button is pressed — stages the new package in the user's data folder.

At the next start the staged copy is put in front of the bundled one, which
means the .exe can update itself without being rebuilt. `apply_staged()` can
also switch a running app over, as long as no download is in progress.
"""

from __future__ import annotations

import importlib
import json
import re
import shutil
import sys
import time
import zipfile
from pathlib import Path

import requests

from . import config
from .i18n import t

PYPI = "https://pypi.org/pypi/yt-dlp/json"
# A successful check is trusted for half a day; a failed one is retried sooner.
CHECK_EVERY = 12 * 3600
RETRY_AFTER = 10 * 60
TIMEOUT = (10, 45)

_VERSION_LINE = re.compile(r"__version__\s*=\s*['\"]([^'\"]+)['\"]")


# --------------------------------------------------------------------- versions


def _key(version: str) -> tuple[int, ...]:
    """2026.10.26 and 2026.10.26.1 compare the way dates should."""
    parts = re.findall(r"\d+", version or "")
    return tuple(int(part) for part in parts) or (0,)


def newer(candidate: str, current: str) -> bool:
    return bool(candidate) and _key(candidate) > _key(current)


def _staged_root() -> Path:
    return config.data_dir() / "ytdlp"


def _cache_path() -> Path:
    return config.data_dir() / "update.json"


def _read_cache() -> dict:
    cached = config.read_json(_cache_path(), {})
    return cached if isinstance(cached, dict) else {}


def _write_cache(payload: dict) -> None:
    try:
        config.write_json(_cache_path(), payload)
    except OSError:
        pass


# ---------------------------------------------------------------------- status


def installed() -> dict:
    """The yt-dlp the app is really using, and where it came from."""
    try:
        yt_dlp = importlib.import_module("yt_dlp")
        version = importlib.import_module("yt_dlp.version").__version__
        location = Path(getattr(yt_dlp, "__file__", "") or "").resolve()
    except Exception:
        return {"version": "", "source": "missing", "location": ""}

    root = _staged_root().resolve()
    staged = location == root / "yt_dlp" or root in location.parents
    return {
        "version": str(version),
        "source": "staged" if staged else ("bundled" if getattr(sys, "frozen", False) else "installed"),
        "location": str(location),
    }


def info(*, allow_network: bool = False) -> dict:
    """Everything the window needs to decide whether to show the notice."""
    cached = _read_cache()
    if allow_network and _due(cached):
        cached = refresh()

    current = installed()
    latest = str(cached.get("latest") or "")
    return {
        **current,
        "latest": latest,
        "outdated": newer(latest, current["version"]),
        "checked_at": float(cached.get("checked_at") or 0),
        "error": _error_text(cached),
    }


def _error_text(cached: dict) -> str:
    """The cached failure, written by whichever language was active at the time."""
    key = str(cached.get("error_key") or "")
    if key:
        return t(key, error=str(cached.get("error_detail") or ""))
    legacy = str(cached.get("error") or "")
    return t(legacy) if legacy else ""


def _due(cached: dict) -> bool:
    last = float(cached.get("checked_at") or 0)
    wait = RETRY_AFTER if _error_text(cached) else CHECK_EVERY
    return time.time() - last >= wait


def refresh() -> dict:
    """Ask PyPI which version is the latest one. Never raises."""
    latest, error_key, error_detail = "", "", ""
    try:
        response = requests.get(PYPI, timeout=TIMEOUT, headers={"Accept": "application/json"})
        response.raise_for_status()
        payload = response.json()
        latest = str((payload.get("info") or {}).get("version") or "")
        if not latest:
            error_key = "update.no_version"
    except Exception as exc:  # offline, rate-limited, PyPI down: all the same to us
        error_key, error_detail = _network_error(exc)
    cached = {
        "checked_at": time.time(),
        "latest": latest,
        "error_key": error_key,
        "error_detail": error_detail,
    }
    _write_cache(cached)
    return cached


def _network_error(exc: Exception) -> tuple[str, str]:
    if isinstance(exc, requests.Timeout):
        return "update.timeout", ""
    if isinstance(exc, requests.RequestException):
        return "update.network", ""
    return "update.failed_detail", str(exc)


# --------------------------------------------------------------------- staging


def _wheel_url(version: str) -> str:
    """Ask PyPI for the pure-Python wheel of one exact version."""
    response = requests.get(
        f"https://pypi.org/pypi/yt-dlp/{version}/json",
        timeout=TIMEOUT,
        headers={"Accept": "application/json"},
    )
    response.raise_for_status()
    files = (response.json() or {}).get("urls") or []
    wheels = [
        item
        for item in files
        if str(item.get("filename") or "").endswith(".whl")
        and str(item.get("packagetype") or "") == "bdist_wheel"
    ]
    wheels.sort(key=lambda item: "py3-none-any" not in str(item.get("filename") or ""))
    if not wheels:
        raise RuntimeError(t("update.no_wheel"))
    return str(wheels[0]["url"])


def download_and_stage(version: str) -> dict:
    """Download the wheel for `version` and unpack it in the data folder."""
    if not version:
        raise RuntimeError(t("update.missing_version"))
    url = _wheel_url(version)
    work = _staged_root()
    work.mkdir(parents=True, exist_ok=True)
    partial = work / f".{version}.part"
    wheel = work / f".{version}.whl"
    _remove(partial)
    _remove(wheel)

    try:
        with requests.get(url, stream=True, timeout=TIMEOUT) as response:
            response.raise_for_status()
            with wheel.open("wb") as handle:
                for chunk in response.iter_content(128 * 1024):
                    if chunk:
                        handle.write(chunk)
        try:
            with zipfile.ZipFile(wheel) as archive:
                names = archive.namelist()
                if not any(name.startswith("yt_dlp/") for name in names):
                    raise RuntimeError(t("update.bad_package"))
                archive.extractall(partial)
        except zipfile.BadZipFile as exc:
            raise RuntimeError(t("update.corrupt")) from exc

        package = partial / "yt_dlp"
        found = _read_version(package / "version.py")
        if not found:
            raise RuntimeError(t("update.no_declared_version"))

        target = work / found
        _remove(target)
        partial.rename(target)
        config.write_json(
            work / "current.json",
            {"version": found, "checked_at": time.time()},
        )
        return {"version": found, "path": str(target)}
    finally:
        _remove(partial)
        _remove(wheel)


def _read_version(path: Path) -> str:
    try:
        match = _VERSION_LINE.search(path.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return ""
    return match.group(1) if match else ""


def _remove(path: Path) -> None:
    try:
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
    except OSError:
        pass


# --------------------------------------------------------------------- activate


def _staged_package() -> Path | None:
    marker = config.read_json(_staged_root() / "current.json", {})
    version = str((marker or {}).get("version") or "") if isinstance(marker, dict) else ""
    if not version:
        return None
    package = _staged_root() / version / "yt_dlp"
    return package if (package / "__init__.py").is_file() else None


def prefer_staged() -> bool:
    """Put a previously staged yt-dlp in front of the bundled one.

    Called once from `app/__init__.py`, before anything imports yt_dlp. The
    meta-path reordering is what makes this work inside a PyInstaller bundle,
    where the frozen importer would otherwise win over sys.path.
    """
    package = _staged_package()
    if package is None:
        return False
    root = str(package.parent)
    if root not in sys.path:
        sys.path.insert(0, root)
    else:
        sys.path.remove(root)
        sys.path.insert(0, root)

    try:
        from importlib.machinery import PathFinder

        for index, finder in enumerate(sys.meta_path):
            if finder is PathFinder and index:
                sys.meta_path.insert(0, sys.meta_path.pop(index))
                break
    except Exception:
        pass
    importlib.invalidate_caches()
    return True


def apply_staged() -> bool:
    """Switch a running process to the staged copy. True when it took effect."""
    if not prefer_staged():
        return False
    importlib.invalidate_caches()
    for name in [name for name in sys.modules if name == "yt_dlp" or name.startswith("yt_dlp.")]:
        del sys.modules[name]
    try:
        importlib.import_module("yt_dlp")
    except Exception:
        return False
    return True


def update() -> dict:
    """Check, then stage the newest release. Raises RuntimeError with words to show."""
    cached = refresh()
    latest = str(cached.get("latest") or "")
    if not latest:
        raise RuntimeError(_error_text(cached) or t("update.check_failed"))

    current = installed()
    if not newer(latest, current["version"]):
        return {**current, "changed": False, "latest": latest}

    staged = download_and_stage(latest)
    applied = apply_staged()
    return {
        **installed(),
        "changed": True,
        "applied": applied,
        "version_installed": staged["version"],
        "latest": latest,
    }
