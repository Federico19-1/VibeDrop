"""Avvio: python run.py — oppure python run.py --serve per il solo server."""

import multiprocessing

from app.main import main

if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(main())
