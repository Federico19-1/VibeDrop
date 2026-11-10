"""Delivery to the phone through the same bot the old script used.

Telegram caps a bot upload at 50 MB, so a bigger file becomes a message with its
path instead — which is also the only thing the old script did with it.
"""

from __future__ import annotations

import os
from pathlib import Path

import requests

from .i18n import t

LIMIT_MB = 50
API = "https://api.telegram.org/bot{token}/{method}"

# Telegram answers in English; these are the answers people actually get, in words
# that say what to fix. The sentences live in app/i18n.py.
_HINTS = (
    ("unauthorized", "telegram.hint_unauthorized"),
    ("chat not found", "telegram.hint_chat"),
    ("bot was blocked", "telegram.hint_blocked"),
    ("bot is not a member", "telegram.hint_member"),
    ("too many requests", "telegram.hint_rate"),
    ("file is too big", "telegram.hint_too_big"),
    ("timed out", "telegram.hint_timeout"),
)


class TelegramError(RuntimeError):
    pass


def _explain(description: str) -> str:
    lowered = (description or "").lower()
    for needle, key in _HINTS:
        if needle in lowered:
            return t(key)
    return description or t("telegram.rejected")


def _call(token: str, method: str, *, data: dict, files: dict | None = None, timeout: int = 120) -> dict:
    if not token:
        raise TelegramError(t("telegram.no_token"))
    try:
        response = requests.post(
            API.format(token=token, method=method),
            data=data,
            files=files,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise TelegramError(
            t("telegram.unreachable", error=exc.__class__.__name__)
        ) from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise TelegramError(
            t("telegram.bad_response", status=response.status_code)
        ) from exc

    if not payload.get("ok"):
        raise TelegramError(_explain(payload.get("description") or f"HTTP {response.status_code}"))
    return payload


def send_audio(token: str, chat_id: str, path: str, caption: str) -> str:
    """'sent' | 'too_big'. Raises TelegramError when Telegram says no."""
    size_mb = os.path.getsize(path) / (1024 * 1024)

    if size_mb > LIMIT_MB:
        _call(
            token,
            "sendMessage",
            data={
                "chat_id": chat_id,
                "text": (
                    f"{caption}\n\n"
                    + t(
                        "telegram.too_big_message",
                        limit=LIMIT_MB,
                        path=Path(path).resolve(),
                    )
                ),
            },
        )
        return "too_big"

    try:
        with open(path, "rb") as handle:
            _call(
                token,
                "sendAudio",
                data={
                    "chat_id": chat_id,
                    "caption": caption,
                    "title": Path(path).stem,
                },
                files={"audio": (Path(path).name, handle, "audio/mpeg")},
                timeout=300,
            )
        return "sent"
    except TelegramError as exc:
        # The download is already safe on disk; tell the phone where it is.
        _call(
            token,
            "sendMessage",
            data={
                "chat_id": chat_id,
                "text": (
                    f"{caption}\n\n"
                    + t(
                        "telegram.send_failed_message",
                        error=exc,
                        path=Path(path).resolve(),
                    )
                ),
            },
        )
        raise


def test_connection(token: str, chat_id: str) -> str:
    """Prove the token and the chat id work, and return the bot's username."""
    payload = _call(token, "getMe", data={})
    bot = (payload.get("result") or {}).get("username") or "bot"
    _call(
        token,
        "sendMessage",
        data={
            "chat_id": chat_id,
            "text": t("telegram.test_message"),
        },
    )
    return bot


def find_chats(token: str) -> list[dict]:
    """Read the chats that already wrote to the bot, so nobody has to hunt for an id.

    Telegram only keeps updates for 24 hours and only when no webhook is set;
    both limits are fine here — the user has just pressed Start on their own bot.
    """
    payload = _call(
        token,
        "getUpdates",
        data={"limit": 100, "allowed_updates": '["message","my_chat_member"]'},
        timeout=25,
    )

    found: dict[str, dict] = {}
    for update in payload.get("result") or []:
        if not isinstance(update, dict):
            continue
        message = (
            update.get("message")
            or update.get("edited_message")
            or update.get("channel_post")
            or update.get("my_chat_member")
            or update.get("chat_member")
            or {}
        )
        chat = message.get("chat") if isinstance(message, dict) else None
        if not isinstance(chat, dict) or chat.get("id") is None:
            continue
        name = " ".join(
            part for part in (chat.get("first_name"), chat.get("last_name")) if part
        )
        name = name or chat.get("title") or chat.get("username") or str(chat["id"])
        found[str(chat["id"])] = {
            "id": str(chat["id"]),
            "name": str(name),
            "type": str(chat.get("type") or ""),
            "username": str(chat.get("username") or ""),
        }

    if not found:
        raise TelegramError(t("telegram.no_chats"))
    # The most recent chat comes last in getUpdates: show it first.
    return list(reversed(list(found.values())))

