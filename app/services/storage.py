"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

import json
from app.services.logger import logger
from app.services.paths import DATA_DIR

SETTINGS_FILE = DATA_DIR / "settings.json"


def save_settings(settings):
    logger.info("Email server settings saved")
    SETTINGS_FILE.parent.mkdir(exist_ok=True)

    with SETTINGS_FILE.open("w", encoding="utf-8") as file:
        json.dump(settings, file, ensure_ascii=False, indent=4)


def load_settings():
    if not SETTINGS_FILE.exists():
        return {}

    try:
        with SETTINGS_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return {}
