"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

import json
import hashlib
from pathlib import Path
from threading import RLock


CHATS_DIR = Path("data/chats")
_STORAGE_LOCK = RLock()


def get_chat_file(contact_address):
    """Возвращает файл диалога для конкретного адреса."""
    contact_id = hashlib.sha256(
        contact_address.lower().encode("utf-8")
    ).hexdigest()

    return CHATS_DIR / f"{contact_id}.json"


def load_messages(contact_address):
    with _STORAGE_LOCK:
        return _load_messages_unlocked(contact_address)


def _load_messages_unlocked(contact_address):
    """Загрузить историю диалога."""
    chat_file = get_chat_file(contact_address)

    if not chat_file.exists():
        return []

    try:
        with chat_file.open("r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return []


def save_message(contact_address, sender, text):
    with _STORAGE_LOCK:
        """Добавить сообщение в историю."""
        CHATS_DIR.mkdir(parents=True, exist_ok=True)

        messages = _load_messages_unlocked(contact_address)

        messages.append({
            "sender": sender,
            "text": text
        })

        chat_file = get_chat_file(contact_address)

        with chat_file.open("w", encoding="utf-8") as file:
            json.dump(messages, file, ensure_ascii=False, indent=4)
