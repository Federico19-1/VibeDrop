"""The queue. One worker thread, one download at a time, newest at the bottom.

The old script processed a list of URLs one after another; this keeps that
behaviour (YouTube is unhappy with parallel downloads from the same IP) and adds
the per-item state the window needs.
"""

from __future__ import annotations

import queue
import threading
import time
import uuid

from . import config
from .downloader import clean_error, download, is_supported, normalize_url
from .i18n import t
from .telegram import TelegramError, send_audio

ACTIVE = ("queued", "downloading", "converting", "sending")
MAX_HISTORY = 80


def _now() -> float:
    return time.time()


def _fmt_duration(seconds: int) -> str:
    total = max(0, int(seconds or 0))
    hours, rest = divmod(total, 3600)
    minutes, secs = divmod(rest, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def _download_details(title: str, duration: int, size_mb: float, template: str) -> str:
    values = {
        "title": title,
        "duration": _fmt_duration(duration),
        "size": f"{size_mb:.1f} MB",
    }
    result = str(template or config.DEFAULT_DOWNLOAD_DETAILS)
    for key, value in values.items():
        result = result.replace(f"{{{key}}}", value)
    return result.strip()


class JobManager:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._jobs: list[dict] = []
        self._by_id: dict[str, dict] = {}
        self._queue: queue.Queue[str] = queue.Queue()
        self._load()
        self._worker = threading.Thread(target=self._run, name="download-worker", daemon=True)
        self._worker.start()

    # ------------------------------------------------------------------ public

    def add(self, urls: list[str]) -> dict:
        added = 0
        rejected: list[str] = []

        for raw in urls:
            url = normalize_url(str(raw))
            if not is_supported(url):
                rejected.append(str(raw).strip())
                continue

            job = {
                "id": uuid.uuid4().hex[:12],
                "url": url,
                "title": "",
                "status": "queued",
                "stage": "queued",
                "progress": None,
                "duration": 0,
                "size_mb": 0.0,
                "file": "",
                "error": "",
                "note": "",
                "telegram": "",
                "created": _now(),
            }
            with self._lock:
                self._jobs.append(job)
                self._by_id[job["id"]] = job
            self._queue.put(job["id"])
            added += 1

        if added:
            self._save()
        return {"added": added, "rejected": rejected}

    def list(self) -> list[dict]:
        with self._lock:
            return [dict(job) for job in self._jobs]

    def get(self, job_id: str) -> dict | None:
        with self._lock:
            job = self._by_id.get(job_id)
            return dict(job) if job else None

    def retry(self, job_id: str) -> dict:
        with self._lock:
            job = self._by_id.get(job_id)
            if job is None:
                raise KeyError(t("job.not_found"))
            if job["status"] in ACTIVE:
                raise ValueError(t("job.active"))
            job.update(
                status="queued",
                stage="queued",
                progress=None,
                error="",
                note="",
                telegram="",
                file="",
            )
        self._queue.put(job_id)
        self._save()
        return dict(job)

    def resend_telegram(self, job_id: str) -> dict:
        with self._lock:
            job = self._by_id.get(job_id)
            if job is None:
                raise KeyError(t("job.not_found"))
            if not job.get("file") or job.get("status") != "done":
                raise ValueError(t("job.not_ready"))
            job["telegram"] = ""
            job["note"] = ""
        settings = config.load_settings()
        if not settings["token"] or not settings["chat_id"]:
            with self._lock:
                job["note"] = t("job.telegram_not_configured")
                job["telegram"] = "failed"
            self._save()
            return dict(job)

        with self._lock:
            job["status"] = "sending"
            job["stage"] = "sending"
        try:
            caption = _download_details(
                job["title"], job["duration"], job["size_mb"], settings["download_details"]
            )
            outcome = send_audio(settings["token"], settings["chat_id"], job["file"], caption)
            with self._lock:
                job["telegram"] = outcome
                job["note"] = t("job.too_big_note") if outcome == "too_big" else ""
        except TelegramError as exc:
            with self._lock:
                job["telegram"] = "failed"
                job["note"] = t("job.telegram_failed", error=exc)
        except Exception as exc:
            with self._lock:
                job["telegram"] = "failed"
                job["note"] = t("job.send_failed", error=clean_error(exc))
        finally:
            with self._lock:
                job["status"] = "done"
                job["stage"] = "done"
                job["progress"] = 100.0
            self._save()
        return dict(job)

    def clear_finished(self) -> dict:
        with self._lock:
            keep = [job for job in self._jobs if job["status"] in ACTIVE]
            removed = len(self._jobs) - len(keep)
            self._jobs = keep
            self._by_id = {job["id"]: job for job in keep}
        self._save()
        return {"removed": removed}

    def delete(self, job_id: str) -> dict:
        with self._lock:
            job = self._by_id.get(job_id)
            if job is None:
                raise KeyError(t("job.not_found"))
            if job["status"] in ACTIVE:
                raise ValueError(t("job.active"))
            self._jobs = [item for item in self._jobs if item["id"] != job_id]
            self._by_id.pop(job_id, None)
        self._save()
        return {"removed": 1}

    def counts(self) -> dict:
        with self._lock:
            active = sum(1 for job in self._jobs if job["status"] in ACTIVE)
            errors = sum(1 for job in self._jobs if job["status"] == "error")
        return {"total": len(self._jobs), "active": active, "errors": errors}

    # ------------------------------------------------------------------ worker

    def _run(self) -> None:
        while True:
            job_id = self._queue.get()
            try:
                job = self._by_id.get(job_id)
                if job is not None:
                    self._process(job)
            except Exception as exc:  # the worker must survive anything
                with self._lock:
                    if job_id in self._by_id:
                        self._by_id[job_id]["status"] = "error"
                        self._by_id[job_id]["error"] = clean_error(exc)
                self._save()
            finally:
                self._queue.task_done()

    def _process(self, job: dict) -> None:
        settings = config.load_settings()
        with self._lock:
            job.update(status="downloading", stage="downloading", progress=0.0, error="", note="")

        def on_progress(stage: str, percent: float | None) -> None:
            with self._lock:
                job["stage"] = stage
                job["status"] = "converting" if stage == "converting" else "downloading"
                if percent is not None:
                    job["progress"] = round(percent, 1)

        try:
            result = download(
                job["url"],
                outdir=settings["output_dir"],
                bitrate=settings["bitrate"],
                on_progress=on_progress,
                cookies=config.cookies_path(),
            )
        except Exception as exc:
            with self._lock:
                job.update(status="error", error=clean_error(exc), progress=None, stage="error")
            self._save()
            return

        with self._lock:
            job.update(
                title=result["title"],
                duration=result["duration"],
                size_mb=round(result["size_mb"], 2),
                file=result["file"],
                progress=100.0,
                stage="sending",
            )

        if not settings["token"] or not settings["chat_id"]:
            with self._lock:
                job["telegram"] = "failed"
                job["note"] = t("job.telegram_not_configured")
        else:
            with self._lock:
                job["status"] = "sending"
            caption = _download_details(
                result["title"], result["duration"], result["size_mb"], settings["download_details"]
            )
            try:
                outcome = send_audio(
                    settings["token"], settings["chat_id"], result["file"], caption
                )
                with self._lock:
                    job["telegram"] = outcome
                    if outcome == "too_big":
                        job["note"] = t("job.too_big_note")
            except TelegramError as exc:
                with self._lock:
                    job["telegram"] = "failed"
                    job["note"] = t("job.telegram_failed", error=exc)
            except Exception as exc:
                with self._lock:
                    job["telegram"] = "failed"
                    job["note"] = t("job.send_failed", error=clean_error(exc))

        with self._lock:
            job.update(status="done", stage="done", progress=100.0)
        self._save()

    # ------------------------------------------------------------------ storage

    def _save(self) -> None:
        with self._lock:
            jobs = [dict(job) for job in self._jobs][-MAX_HISTORY:]
        try:
            config.write_json(config.state_path(), {"version": 1, "jobs": jobs})
        except OSError:
            pass  # a full disk must not stop a download

    def _load(self) -> None:
        stored = config.read_json(config.state_path(), {})
        jobs = stored.get("jobs") if isinstance(stored, dict) else None
        if not isinstance(jobs, list):
            return
        for job in jobs[-MAX_HISTORY:]:
            if not isinstance(job, dict) or "id" not in job or "url" not in job:
                continue
            cleaned = {
                "id": str(job.get("id")),
                "url": str(job.get("url")),
                "title": str(job.get("title") or ""),
                "status": str(job.get("status") or "error"),
                "stage": str(job.get("stage") or ""),
                "progress": job.get("progress"),
                "duration": int(job.get("duration") or 0),
                "size_mb": float(job.get("size_mb") or 0),
                "file": str(job.get("file") or ""),
                "error": str(job.get("error") or ""),
                "note": str(job.get("note") or ""),
                "telegram": str(job.get("telegram") or ""),
                "created": float(job.get("created") or 0),
            }
            if cleaned["status"] in ACTIVE:
                cleaned["status"] = "error"
                cleaned["error"] = t("job.interrupted")
            self._jobs.append(cleaned)
            self._by_id[cleaned["id"]] = cleaned
