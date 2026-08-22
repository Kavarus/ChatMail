"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from pathlib import Path
from kivy.utils import platform


def get_data_dir() -> Path:
    if platform == "android":
        from android.storage import app_storage_path  # type: ignore
        path = Path(app_storage_path())
    else:
        from kivy.app import App

        running_app = App.get_running_app()
        if running_app is not None:
            path = Path(running_app.user_data_dir)
        else:
            path = (Path(__file__).resolve().parents[2] / "data")

    path.mkdir(parents=True, exist_ok=True)
    return path


DATA_DIR = get_data_dir()
LOCALES_DIR = DATA_DIR / "locales"
LOCALES_DIR.mkdir(parents=True, exist_ok=True)
