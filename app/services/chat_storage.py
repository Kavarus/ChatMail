"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

import json
from threading import RLock
from datetime import datetime, timezone
from app.services.logger import logger
from app.services.paths import DATA_DIR

CHATS_DIR = DATA_DIR / "chats"
_STORAGE_LOCK = RLock()


def get_chat_file(contact_guid):
    return CHATS_DIR / f"{contact_guid}.json"


def load_messages(contact_guid):
    with _STORAGE_LOCK:
        return _load_messages_unlocked(contact_guid)


def _load_messages_unlocked(contact_guid):
    """Загрузить историю диалога."""
    chat_file = get_chat_file(contact_guid)

    if not chat_file.exists():
        return []

    try:
        with chat_file.open("r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return []


def save_message(contact_guid, direction, text, created_at=None):
    """
    direction: "in" / "out"
    """
    if direction not in ("in", "out"):
        raise ValueError("Invalid direction")

    if created_at is None:
        created_at = datetime.now(timezone.utc).isoformat()

    with _STORAGE_LOCK:
        """Добавить сообщение в историю."""
        CHATS_DIR.mkdir(parents=True, exist_ok=True)

        messages = _load_messages_unlocked(contact_guid)
        messages.append({
            "direction": direction,
            "text": text,
            "created_at": created_at,
        })

        chat_file = get_chat_file(contact_guid)
        temporary_file = chat_file.with_suffix(".tmp")
        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump(messages, file, ensure_ascii=False, indent=4)
        temporary_file.replace(chat_file)


def delete_messages(contact_guid):
    """Удаляет файл истории чата контакта."""
    with _STORAGE_LOCK:
        chat_file = get_chat_file(contact_guid)

        try:
            chat_file.unlink(missing_ok=True)
        except OSError:
            logger.exception(f"File delete is failing: {chat_file}")
            raise
