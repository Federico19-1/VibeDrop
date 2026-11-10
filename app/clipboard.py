"""Reading the system clipboard for the "Paste" buttons in Settings.

The window tries the browser Clipboard API first; when that is blocked (some
WebView2 builds, or a browser without permission) the server reads the clipboard
itself. Windows uses the Win32 API through ctypes, everything else falls back to
the usual command-line helpers.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import sys
import time


class ClipboardBusy(RuntimeError):
    """Another program is holding the clipboard open."""


def read_text() -> str:
    if os.name == "nt":
        return _read_windows()
    return _read_commandline()


def write_text(text: str) -> None:
    if os.name == "nt":
        _write_windows(text)
        return
    for command in (("xclip", "-selection", "clipboard"), ("xsel", "--clipboard", "--input")):
        try:
            result = subprocess.run(command, input=text, text=True, timeout=3, check=False)
        except (FileNotFoundError, subprocess.SubprocessError):
            continue
        if result.returncode == 0:
            return
    raise OSError(f"no clipboard command on {sys.platform}")


# --------------------------------------------------------------------- windows

_CF_UNICODETEXT = 13
_CF_TEXT = 1


def _read_windows() -> str:
    from ctypes import wintypes

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    user32.OpenClipboard.argtypes = [wintypes.HWND]
    user32.OpenClipboard.restype = wintypes.BOOL
    user32.CloseClipboard.argtypes = []
    user32.CloseClipboard.restype = wintypes.BOOL
    user32.IsClipboardFormatAvailable.argtypes = [wintypes.UINT]
    user32.IsClipboardFormatAvailable.restype = wintypes.BOOL
    user32.GetClipboardData.argtypes = [wintypes.UINT]
    user32.GetClipboardData.restype = wintypes.HANDLE
    kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalUnlock.restype = wintypes.BOOL

    opened = False
    for _ in range(8):  # another app may hold it for a few milliseconds
        if user32.OpenClipboard(None):
            opened = True
            break
        time.sleep(0.04)
    if not opened:
        raise ClipboardBusy("clipboard busy")

    try:
        if user32.IsClipboardFormatAvailable(_CF_UNICODETEXT):
            handle = user32.GetClipboardData(_CF_UNICODETEXT)
            encoding = "utf-16-le"
        elif user32.IsClipboardFormatAvailable(_CF_TEXT):
            handle = user32.GetClipboardData(_CF_TEXT)
            encoding = "mbcs"
        else:
            return ""

        if not handle:
            return ""
        pointer = kernel32.GlobalLock(handle)
        if not pointer:
            return ""
        try:
            return ctypes.wstring_at(pointer) if encoding == "utf-16-le" else _ansi_text(pointer)
        finally:
            kernel32.GlobalUnlock(handle)
    finally:
        user32.CloseClipboard()


def _write_windows(text: str) -> None:
    from ctypes import wintypes

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    user32.OpenClipboard.argtypes = [wintypes.HWND]
    user32.OpenClipboard.restype = wintypes.BOOL
    user32.CloseClipboard.argtypes = []
    user32.EmptyClipboard.argtypes = []
    user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
    kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
    kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]

    for _ in range(8):
        if user32.OpenClipboard(None):
            break
        time.sleep(0.04)
    else:
        raise ClipboardBusy("clipboard busy")

    payload = (str(text) + "\0").encode("utf-16-le")
    handle = kernel32.GlobalAlloc(0x0002, len(payload))
    if not handle:
        user32.CloseClipboard()
        raise OSError("clipboard allocation failed")
    pointer = kernel32.GlobalLock(handle)
    if not pointer:
        user32.CloseClipboard()
        raise OSError("clipboard lock failed")
    try:
        ctypes.memmove(pointer, payload, len(payload))
    finally:
        kernel32.GlobalUnlock(handle)
    try:
        user32.EmptyClipboard()
        if not user32.SetClipboardData(_CF_UNICODETEXT, handle):
            raise OSError("clipboard write failed")
        handle = None
    finally:
        user32.CloseClipboard()
        if handle:
            kernel32.GlobalFree(handle)


def _ansi_text(pointer) -> str:
    raw = ctypes.string_at(pointer)
    try:
        return raw.decode("mbcs", errors="replace")
    except LookupError:
        return raw.decode("latin-1", errors="replace")


# --------------------------------------------------------------------- others

_COMMANDS = (
    ("pbpaste",),
    ("wl-paste", "--no-newline"),
    ("xclip", "-selection", "clipboard", "-o"),
    ("xsel", "--clipboard", "--output"),
)


def _read_commandline() -> str:
    for command in _COMMANDS:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
            )
        except (FileNotFoundError, subprocess.SubprocessError):
            continue
        if result.returncode == 0:
            return result.stdout
    raise OSError(f"no clipboard command on {sys.platform}")
