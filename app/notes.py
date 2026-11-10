"""A small personal note sheet, saved next to the settings.

One list, no folders, no sync: write a line, delete it when the song has been
downloaded. It is deliberately plain — a place to hold the URLs and titles you
do not want to forget before they make it into the queue.
"""

from __future__ import annotations

import time
import uuid

from . import config
from .i18n import t

MAX_NOTES = 200
MAX_LENGTH = 2000


def _path():
    return config.data_dir() / "notes.json"


def list_notes() -> list[dict]:
    stored = config.read_json(_path(), {})
    notes = stored.get("notes") if isinstance(stored, dict) else None
    if not isinstance(notes, list):
        return []
    cleaned = []
    for note in notes:
        if not isinstance(note, dict):
            continue
        legacy_text = str(note.get("text") or "").strip()
        title = str(note.get("title") or "").strip()
        body = str(note.get("body") or "").strip()
        if not title and legacy_text:
            title, _, body = legacy_text.partition("\n")
        if not title:
            continue
        cleaned.append(
            {
                "id": str(note.get("id") or uuid.uuid4().hex[:10]),
                "title": title[:240],
                "body": body[:MAX_LENGTH],
                "text": "\n".join(part for part in (title, body) if part),
                "created": float(note.get("created") or 0),
            }
        )
    return cleaned[-MAX_NOTES:]


def add(*, title: str = "", body: str = "", raw: str = "") -> dict:
    """Create one song note, or preserve the legacy one-line import behavior."""
    title = str(title or "").strip()
    body = str(body or "").strip()
    if title:
        notes = list_notes()
        if len(notes) >= MAX_NOTES:
            raise ValueError(t("note.full", max=MAX_NOTES))
        notes.append({
            "id": uuid.uuid4().hex[:10],
            "title": title[:240],
            "body": body[:MAX_LENGTH],
            "text": "\n".join(part for part in (title[:240], body[:MAX_LENGTH]) if part),
            "created": time.time(),
        })
        _save(notes)
        return {"added": 1, "notes": notes}

    lines = [line.strip() for line in str(raw or "").splitlines()]
    texts = [line for line in lines if line]
    if not texts:
        raise ValueError(t("note.empty"))

    notes = list_notes()
    room = MAX_NOTES - len(notes)
    if room <= 0:
        raise ValueError(t("note.full", max=MAX_NOTES))
    texts = texts[:room]

    created = time.time()
    added = [
        {
            "id": uuid.uuid4().hex[:10],
            "title": text[:240],
            "body": "",
            "text": text[:MAX_LENGTH],
            "created": created + index / 1000,
        }
        for index, text in enumerate(texts)
    ]
    notes.extend(added)
    _save(notes)
    return {"added": len(added), "notes": notes}


def update(note_id: str, *, title: str, body: str) -> list[dict]:
    note_id = str(note_id or "").strip()
    title = str(title or "").strip()
    body = str(body or "").strip()
    if not note_id:
        raise ValueError(t("note.missing"))
    if not title:
        raise ValueError(t("note.empty"))
    notes = list_notes()
    for note in notes:
        if note["id"] == note_id:
            note["title"] = title[:240]
            note["body"] = body[:MAX_LENGTH]
            note["text"] = "\n".join(part for part in (note["title"], note["body"]) if part)
            _save(notes)
            return notes
    raise KeyError(t("note.not_found"))


def delete(note_id: str) -> list[dict]:
    note_id = str(note_id or "").strip()
    if not note_id:
        raise ValueError(t("note.missing"))
    notes = list_notes()
    kept = [note for note in notes if note["id"] != note_id]
    if len(kept) == len(notes):
        raise KeyError(t("note.not_found"))
    _save(kept)
    return kept


def clear() -> list[dict]:
    _save([])
    return []


def _save(notes: list[dict]) -> None:
    config.write_json(_path(), {"version": 1, "notes": notes[-MAX_NOTES:]})
