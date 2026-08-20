"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

import json
from threading import RLock
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


def save_message(contact_guid, direction, text):
    """
    direction: "in" / "out"
    """
    if direction not in ("in", "out"):
        raise ValueError("Invalid direction")

    with _STORAGE_LOCK:
        """Добавить сообщение в историю."""
        CHATS_DIR.mkdir(parents=True, exist_ok=True)

        messages = _load_messages_unlocked(contact_guid)

        messages.append({
            "direction": direction,
            "text": text,
        })

        chat_file = get_chat_file(contact_guid)

        with chat_file.open("w", encoding="utf-8") as file:
            json.dump(messages, file, ensure_ascii=False, indent=4)
