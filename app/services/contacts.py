"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

import json
from app.models.contact import Contact
from app.services.paths import DATA_DIR

CONTACTS_FILE = DATA_DIR / "contacts.json"


def load_contacts():
    """Загрузить список контактов."""
    if not CONTACTS_FILE.exists():
        return []

    try:
        with CONTACTS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return [Contact.from_dict(item) for item in data]

    except (json.JSONDecodeError, KeyError):
        return []


def save_contacts(contacts):
    """Сохранить список контактов."""
    CONTACTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    data = [contact.to_dict() for contact in contacts]

    with CONTACTS_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def add_contact(name, address):
    """Добавить контакт и сохранить список."""
    contacts = load_contacts()

    contact = Contact(
        name=name.strip(),
        email=address.strip()
    )

    contacts.append(contact)
    save_contacts(contacts)

    return contact
