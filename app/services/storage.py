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
PENDING_DELETE_IDS_FILE = DATA_DIR / "pending_delete_ids.json"
REQUIRED_MAIL_SETTINGS = (
    "user",
    "password",
    "imap_server",
    "imap_port",
)
DEFAULT_APPLICATION_SETTINGS = {
    "active_mail_interval": 45,
    "background_mail_interval": 300,
    "language": "ru",
}


def is_first_run(settings):
    return not bool(settings.get("terms_accepted", False))


def default_settings():
    return {
        "application": DEFAULT_APPLICATION_SETTINGS.copy(),
        "connection": {},
        "terms_accepted": False,
    }


def save_settings(settings):
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with SETTINGS_FILE.open("w", encoding="utf-8") as file:
        json.dump(settings, file, ensure_ascii=False, indent=4)
    logger.info("Email server settings saved")


def load_settings():
    if not SETTINGS_FILE.exists():
        return default_settings()

    try:
        with SETTINGS_FILE.open("r", encoding="utf-8") as file:
            settings = json.load(file)
        return normalize_settings(settings)
    except (OSError, json.JSONDecodeError):
        return {}


def normalize_settings(settings):
    result = default_settings()

    application = settings.get("application", {})
    connection = settings.get("connection", {})

    if isinstance(application, dict):
        result["application"].update(application)

    if isinstance(connection, dict):
        result["connection"].update(connection)

    result["terms_accepted"] = bool(settings.get("terms_accepted", False))

    return result


def accept_terms(language):
    from app.services.i18n import i18n
    if language not in i18n.get_available_languages():
        language = i18n.language

    settings = load_settings()
    settings["application"]["language"] = language
    settings["terms_accepted"] = True
    save_settings(settings)


def get_application_settings(settings=None):
    settings = settings or load_settings()

    application = DEFAULT_APPLICATION_SETTINGS.copy()
    application.update(settings.get("application", {}))

    return application


def get_connection_settings(settings=None):
    settings = settings or load_settings()
    return settings.get("connection", {}).copy()


def has_mail_settings(settings):
    connection = get_connection_settings(settings)

    return bool(connection) and all(
        str(connection.get(key, "")).strip()
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


def save_pending_delete_ids(message_ids):
    logger.info("Save pending delete ids")
    PENDING_DELETE_IDS_FILE.parent.mkdir(parents=True, exist_ok=True)

    temporary_file = PENDING_DELETE_IDS_FILE.with_suffix(".tmp")

    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(sorted(message_ids), file, ensure_ascii=False, indent=4)

    temporary_file.replace(PENDING_DELETE_IDS_FILE)


def load_pending_delete_ids():
    if not PENDING_DELETE_IDS_FILE.exists():
        return set()

    try:
        with PENDING_DELETE_IDS_FILE.open("r", encoding="utf-8") as file:
            return set(json.load(file))
    except (OSError, json.JSONDecodeError):
        return set()


def get_saved_language(settings):
    from app.services.i18n import i18n
    application = get_application_settings(settings)
    language = application.get("language", DEFAULT_APPLICATION_SETTINGS["language"])
    available_languages = i18n.get_available_languages()
    if language in available_languages:
        return language

    return available_languages[0] if available_languages else DEFAULT_APPLICATION_SETTINGS["language"]
