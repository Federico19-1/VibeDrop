"""A tiny HTTP server bound to 127.0.0.1.

The window is only a browser pointed at this server, which is why the same UI can
later run on a phone through Termux without rewriting anything.
"""

from __future__ import annotations

import json
import mimetypes
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from . import __version__, clipboard, config, notes, updates
from .downloader import ffmpeg_location
from .i18n import t
from .telegram import TelegramError, find_chats, test_connection

UI_DIR = (Path(__file__).resolve().parent.parent / "ui").resolve()


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, manager):
        super().__init__(address, Handler)
        self.manager = manager

    def handle_error(self, request, client_address):
        if isinstance(sys.exc_info()[1], (ConnectionError, TimeoutError)):
            return  # a window closing is not worth a traceback
        super().handle_error(request, client_address)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = f"VibeDrop/{__version__}"
    sys_version = ""

    def log_message(self, *args):  # the window has its own log; keep the console clean
        pass

    # ------------------------------------------------------------------ replies

    def _send(self, status: int, body: bytes, ctype: str, *, cache: bool = False) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "public, max-age=86400" if cache else "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        try:
            self.end_headers()
            self.wfile.write(body)
        except (ConnectionError, TimeoutError):
            pass  # the window was closed while replying

    def _json(self, payload, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def _error(self, message: str, status: int = 400) -> None:
        self._json({"error": message}, status)

    def _body(self) -> dict:
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length <= 0:
            return {}
        if length > 1_000_000:
            raise ValueError(t("request.too_large"))
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as exc:
            raise ValueError(t("json.invalid")) from exc
        if not isinstance(data, dict):
            raise ValueError(t("json.invalid"))
        return data

    # ------------------------------------------------------------------ routes

    def do_GET(self):
        path = urlparse(self.path).path
        if not path.startswith("/api/"):
            return self._static(path)
        try:
            if path == "/api/state":
                return self._json(self._state())
            if path == "/api/health":
                return self._json({"ok": True, "version": __version__, "ytdlp": updates.info()["version"]})
            return self._error(t("endpoint.unknown"), 404)
        except Exception as exc:
            return self._error(str(exc) or t("server.internal"), 500)

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            data = self._body()
            return self._post(path, data)
        except ValueError as exc:
            return self._error(str(exc), 400)
        except KeyError as exc:
            # Every KeyError raised by the routes is a job that no longer exists.
            return self._error(str(exc).strip("'\"") or t("job.not_found"), 404)
        except FileNotFoundError as exc:
            return self._error(str(exc) or t("file.not_found"), 404)
        except TelegramError as exc:
            return self._error(str(exc), 400)
        except Exception as exc:
            return self._error(str(exc) or t("server.internal"), 500)

    def _post(self, path: str, data: dict):
        manager = self.server.manager

        if path == "/api/jobs":
            urls = data.get("urls") or []
            if not isinstance(urls, list):
                raise ValueError(t("urls.not_list"))
            result = manager.add([str(url) for url in urls])
            return self._json({**result, "jobs": manager.list()})

        if path == "/api/jobs/retry":
            manager.retry(_require_id(data))
            return self._json({"jobs": manager.list()})

        if path in {"/api/jobs/send-again", "/api/jobs/send_again", "/api/jobs/resend"}:
            manager.resend_telegram(_require_id(data))
            return self._json({"jobs": manager.list()})

        if path == "/api/jobs/reveal":
            job = _job_or_fail(manager, data)
            reveal(Path(job["file"]).parent if job.get("file") else _output_dir())
            return self._json({"ok": True})

        if path == "/api/jobs/play":
            job = _job_or_fail(manager, data)
            opened = play(Path(job["file"]))
            return self._json({"ok": True, "opened": opened})

        if path == "/api/jobs/clear":
            return self._json(manager.clear_finished())

        if path == "/api/jobs/delete":
            manager.delete(_require_id(data))
            return self._json({"jobs": manager.list()})

        if path == "/api/settings":
            saved = config.save_settings(data)
            return self._json({"settings": saved})

        if path == "/api/telegram/test":
            token = str(data.get("token") or "").strip()
            chat_id = str(data.get("chat_id") or "").strip()
            if not token or not chat_id:
                raise ValueError(t("telegram.token_chat_required"))
            return self._json({"bot": test_connection(token, chat_id)})

        if path == "/api/telegram/chats":
            token = str(data.get("token") or "").strip()
            if not token:
                raise ValueError(t("telegram.token_required"))
            return self._json({"chats": find_chats(token)})

        if path == "/api/clipboard/read":
            try:
                return self._json({"text": clipboard.read_text()})
            except clipboard.ClipboardBusy as exc:
                raise ValueError(t("clipboard.busy")) from exc
            except Exception as exc:
                raise ValueError(t("clipboard.unavailable")) from exc

        if path == "/api/clipboard/write":
            text = str(data.get("text") or "")
            if not text:
                raise ValueError(t("clipboard.empty"))
            try:
                clipboard.write_text(text)
            except clipboard.ClipboardBusy as exc:
                raise ValueError(t("clipboard.busy")) from exc
            except Exception as exc:
                raise ValueError(t("clipboard.unavailable")) from exc
            return self._json({"ok": True})

        if path == "/api/notes":
            result = notes.add(
                title=str(data.get("title") or ""),
                body=str(data.get("body") or ""),
                raw=str(data.get("text") or ""),
            )
            return self._json({**result, "notes": result["notes"]})

        if path == "/api/notes/update":
            return self._json({
                "notes": notes.update(
                    str(data.get("id") or ""),
                    title=str(data.get("title") or ""),
                    body=str(data.get("body") or ""),
                ),
            })

        if path == "/api/notes/delete":
            note_id = str(data.get("id") or "").strip()
            return self._json({"notes": notes.delete(note_id)})

        if path == "/api/notes/clear":
            return self._json({"notes": notes.clear()})

        if path == "/api/ytdlp/check":
            updates.refresh()
            return self._json({"ytdlp": updates.info()})

        if path == "/api/ytdlp/update":
            active = manager.counts()["active"]
            if active:
                raise ValueError(t("update.active"))
            return self._json({"ytdlp": {**updates.update(), **updates.info()}})

        if path == "/api/folder/open":
            reveal(Path(_output_dir()))
            return self._json({"ok": True})

        if path == "/api/folder/choose":
            selected = choose_folder(str(data.get("current") or _output_dir()))
            if selected is None:
                return self._json({"path": ""})
            return self._json({"path": str(selected)})

        return self._error(t("endpoint.unknown"), 404)

    # ------------------------------------------------------------------ helpers

    def _state(self) -> dict:
        manager = self.server.manager
        settings = config.load_settings()
        return {
            "jobs": manager.list(),
            "counts": manager.counts(),
            "settings": settings,
            "notes": notes.list_notes(),
            "ffmpeg": bool(ffmpeg_location()),
            "ytdlp": updates.info(),
            "version": __version__,
        }

    def _static(self, path: str) -> None:
        relative = "index.html" if path in ("", "/") else path.lstrip("/")
        target = (UI_DIR / relative).resolve()
        if target != UI_DIR and UI_DIR not in target.parents:
            return self._error(t("file.not_found"), 404)
        if not target.is_file():
            return self._error(t("file.not_found"), 404)

        ctype = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if target.suffix == ".css":
            ctype = "text/css"
        elif target.suffix == ".js":
            ctype = "text/javascript"
        elif target.suffix == ".woff2":
            ctype = "font/woff2"
        if ctype.startswith("text/") or ctype == "application/javascript":
            ctype = f"{ctype}; charset=utf-8"
        self._send(
            200,
            target.read_bytes(),
            ctype,
            cache=target.suffix in (".woff2", ".css"),
        )


def _require_id(data: dict) -> str:
    job_id = str(data.get("id") or "").strip()
    if not job_id:
        raise ValueError(t("job.id_missing"))
    return job_id


def _job_or_fail(manager, data: dict) -> dict:
    job = manager.get(_require_id(data))
    if job is None:
        raise KeyError(t("job.not_found"))
    return job


def _output_dir() -> Path:
    folder = Path(config.load_settings()["output_dir"]).expanduser()
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def choose_folder(initial: str) -> Path | None:
    """Open the platform folder picker and return the selected directory."""
    if os.name != "nt":
        return None
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        selected = filedialog.askdirectory(initialdir=initial, title="Choose download folder")
        root.destroy()
        return Path(selected).expanduser() if selected else None
    except Exception as exc:
        raise ValueError(f"Folder picker unavailable: {exc}") from exc


def reveal(path: Path) -> None:
    """Show a file in the system file manager, or the folder when it is gone."""
    path = Path(path)
    if not path.exists():
        path = path.parent
    is_file = path.is_file()

    if os.name == "nt":
        if is_file:
            subprocess.Popen(["explorer", f"/select,{path}"])
        else:
            os.startfile(str(path))
    elif sys.platform == "darwin":
        subprocess.Popen(["open", "-R", str(path)] if is_file else ["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path.parent if is_file else path)])


def play(path: Path) -> bool:
    if not Path(path).is_file():
        return False
    if os.name == "nt":
        os.startfile(str(path))
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])
    return True


def create_server(manager, port: int = 8756, attempts: int = 25) -> LocalServer:
    last_error: OSError | None = None
    for candidate in range(port, port + attempts):
        try:
            return LocalServer(("127.0.0.1", candidate), manager)
        except OSError as exc:
            last_error = exc
    if port == 0:
        return LocalServer(("127.0.0.1", 0), manager)
    raise RuntimeError(f"Nessuna porta libera fra {port} e {port + attempts}: {last_error}")


def start(server: LocalServer) -> str:
    thread = threading.Thread(target=server.serve_forever, name="http", daemon=True)
    thread.start()
    return f"http://127.0.0.1:{server.server_address[1]}/"
