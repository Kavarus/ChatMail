"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

import json
from uuid import uuid4
from app.services.i18n import i18n
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

    temporary_file = CONTACTS_FILE.with_suffix(".tmp")
    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    temporary_file.replace(CONTACTS_FILE)


def add_contact(name, address):
    """Добавить контакт и сохранить список."""
    contacts = load_contacts()

    normalized_address = address.strip().lower()
    for contact in contacts:
        if contact.email.lower() == normalized_address:
            raise ValueError(
                "Контакт с таким адресом уже существует"
            )

    contact = Contact(
        name=name.strip(),
        email=normalized_address,
        guid=str(uuid4()),
        has_new_messages=False,
    )

    contacts.append(contact)
    save_contacts(contacts)

    return contact


def update_contact(guid, name, address):
    contacts = load_contacts()

    normalized_address = address.strip().lower()
    for contact in contacts:
        if (
            contact.email.lower() == normalized_address
            and contact.guid != guid
        ):
            raise ValueError(
                "Другой контакт уже использует этот адрес"
            )

    for contact in contacts:
        if contact.guid == guid:
            contact.name = name.strip()
            contact.email = normalized_address
            save_contacts(contacts)
            return contact

    raise ValueError("Контакт не найден")


def delete_contact(guid):
    """Удаляет контакт и возвращает удалённый объект."""
    contacts = load_contacts()

    for index, contact in enumerate(contacts):
        if contact.guid == guid:
            deleted_contact = contacts.pop(index)
            save_contacts(contacts)
            return deleted_contact

    raise ValueError("Контакт не найден")


def mark_contact_as_read(guid):
    contacts = load_contacts()

    for contact in contacts:
        if contact.guid == guid:
            contact.has_new_messages = False
            save_contacts(contacts)
            return contact

    return None
