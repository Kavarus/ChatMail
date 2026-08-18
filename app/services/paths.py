"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from pathlib import Path
import sys


def get_data_dir() -> Path:
    # Android и уже запущенное Kivy-приложение
    try:
        from kivy.app import App

        running_app = App.get_running_app()
        if running_app is not None:
            path = Path(running_app.user_data_dir)
            path.mkdir(parents=True, exist_ok=True)
            return path
    except Exception:
        pass

    # Запуск на ПК из редактора
    # Корень проекта: .../chatmail/
    project_dir = Path(__file__).resolve().parents[2]
    path = project_dir / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


DATA_DIR = get_data_dir()
