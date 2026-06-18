"""
paths.py — resource/data path resolution that works both:
  - as a normal Python script (dev mode, or under gunicorn/start_server.sh), and
  - frozen inside a PyInstaller .app bundle (desktop build)

Why this exists:
  Inside a frozen .app, the executable's working directory and __file__
  semantics change, and the bundle itself is read-only once shipped. So:
    - READ-ONLY assets (templates, static files, lb15.txt, q115.txt) must be
      looked up relative to the bundle's extracted resource dir.
    - WRITABLE runtime files (uploads, generated anomaly overlays) must live
      somewhere outside the bundle, or writes will fail / pollute the app.
"""

import os
import sys


def get_base_path():
    """Directory containing bundled READ-ONLY resources."""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS  # PyInstaller's extracted resource dir
    return os.path.dirname(os.path.abspath(__file__))


def get_app_data_dir():
    """Directory for WRITABLE runtime files (uploads/outputs)."""
    if getattr(sys, "frozen", False):
        # Packaged desktop app — write outside the read-only bundle
        home = os.path.expanduser("~")
        data_dir = os.path.join(home, "Library", "Application Support", "CMAD")
        os.makedirs(data_dir, exist_ok=True)
        return data_dir
    # Dev mode / gunicorn deployment — keep original behavior (relative to app.py)
    return os.path.dirname(os.path.abspath(__file__))
