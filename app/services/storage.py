"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

import json
from app.services.logger import logger
from app.services.paths import DATA_DIR

SETTINGS_FILE = DATA_DIR / "settings.json"
PROCESSED_IDS_FILE = DATA_DIR / "processed_message_ids.json"
REQUIRED_MAIL_SETTINGS = (
    "user",
    "password",
    "imap_server",
    "imap_port",
)


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


def has_mail_settings(settings):
    if not settings:
        return False

    return all(
        str(settings.get(key, "")).strip()
        for key in REQUIRED_MAIL_SETTINGS
    )


def save_processed_ids(processed_ids):
    PROCESSED_IDS_FILE.parent.mkdir(parents=True, exist_ok=True)

    temporary_file = PROCESSED_IDS_FILE.with_suffix(".tmp")

    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(list(processed_ids), file, ensure_ascii=False, indent=4)

    temporary_file.replace(PROCESSED_IDS_FILE)


def load_processed_ids():
    if not PROCESSED_IDS_FILE.exists():
        return set()

    try:
        with PROCESSED_IDS_FILE.open("r", encoding="utf-8") as file:
            return set(json.load(file))
    except (OSError, json.JSONDecodeError):
        return set()
