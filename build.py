"""Costruisce l'eseguibile: python build.py

Produce dist/VibeDrop.exe, un file unico che contiene Python, l'interfaccia
e le librerie. Per la conversione in MP3 serve ffmpeg:
  - metti ffmpeg.exe in bin/ prima di lanciare lo script e viene incluso, oppure
  - lascialo fuori e l'app userà l'ffmpeg già presente sul PC.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NAME = "VibeDrop"


def main() -> int:
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("Manca PyInstaller. Installa prima:\n\n    pip install pyinstaller\n")
        return 1

    separator = ";" if os.name == "nt" else ":"
    args = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name",
        NAME,
        "--add-data",
        f"{ROOT / 'ui'}{separator}ui",
        "--collect-all",
        "webview",
        "--hidden-import",
        "webview.platforms.edgechromium",
        # yt-dlp is imported lazily (so an update staged at runtime can win) and
        # through importlib; PyInstaller would otherwise leave it out.
        "--collect-all",
        "yt_dlp",
    ]

    icon = ROOT / "assets" / "vibedrop.ico"
    if icon.is_file():
        args += ["--icon", str(icon)]
        print(f"Icona inclusa: {icon}")
    else:
        print("Nessuna assets/vibedrop.ico: l'eseguibile userà l'icona predefinita.")

    ffmpeg = ROOT / "bin" / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
    if ffmpeg.is_file():
        args += ["--add-binary", f"{ffmpeg}{separator}bin"]
        print(f"ffmpeg incluso: {ffmpeg}")
    else:
        print("Nessun bin/ffmpeg.exe: l'eseguibile userà l'ffmpeg installato sul PC.")

    args.append(str(ROOT / "run.py"))
    print("Costruisco…")
    result = subprocess.run(args, cwd=ROOT)
    if result.returncode != 0:
        return result.returncode

    exe = ROOT / "dist" / f"{NAME}.exe"
    if exe.is_file():
        size = exe.stat().st_size / (1024 * 1024)
        print(f"\nFatto: {exe} ({size:.1f} MB)")
        print("Aprilo con doppio clic: non serve Python né WSL.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
