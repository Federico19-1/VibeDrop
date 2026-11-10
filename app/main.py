"""Entry point: start the local server, then open the window on it.

`python run.py`            the app
`python run.py --serve`    only the server, and the URL is printed (tests, Termux)
"""

from __future__ import annotations

import argparse
import sys
import threading
import webbrowser
from pathlib import Path

from . import __version__, config, updates
from .jobs import JobManager
from .server import create_server, start


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="estrattore-audio",
        description="Scarica l'audio dei video YouTube in MP3, con una finestra.",
    )
    parser.add_argument("--serve", action="store_true", help="avvia solo il server locale")
    parser.add_argument("--port", type=int, default=8756, help="porta locale (default 8756)")
    parser.add_argument("--version", action="version", version=__version__)
    return parser.parse_args(argv)


def window_background() -> str:
    """The colour behind the window while the page loads, without a dark flash."""
    theme = str(config.load_settings().get("theme") or "dark")
    if theme == "system":
        theme = "light" if _system_is_light() else "dark"
    return "#f5f7fb" if theme == "light" else "#0a0d14"


def _system_is_light() -> bool:
    if sys.platform != "win32":
        return False
    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        ) as key:
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return bool(value)
    except Exception:
        return False


def main(argv=None) -> int:
    args = parse_args(argv)

    config.data_dir().mkdir(parents=True, exist_ok=True)
    Path(config.load_settings()["output_dir"]).expanduser().mkdir(parents=True, exist_ok=True)

    manager = JobManager()
    server = create_server(manager, port=args.port)
    url = start(server)

    # Ask PyPI in the background: the window must open instantly, online or not.
    threading.Thread(
        target=updates.info,
        kwargs={"allow_network": True},
        name="ytdlp-check",
        daemon=True,
    ).start()

    if args.serve:
        print(url, flush=True)
        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            pass
        return 0

    try:
        import webview

        webview.create_window(
            "VibeDrop",
            url,
            width=1120,
            height=780,
            min_size=(880, 560),
            background_color=window_background(),
        )
        webview.start()
        return 0
    except Exception as exc:  # no WebView2, no pythonnet, an old Windows
        print(f"Finestra non disponibile ({exc}).", file=sys.stderr)
        print(f"Apro l'interfaccia nel browser: {url}", file=sys.stderr)
        webbrowser.open(url)
        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            pass
        return 0
