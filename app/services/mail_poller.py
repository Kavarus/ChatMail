"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from app.services.mail_reader import read_new_messages
from app.services.chat_storage import save_message
from app.services.contacts import load_contacts


def normalize_email(value: str) -> str:
    return value.strip().lower()


class MailPoller:
    def __init__(self, settings):
        self.settings = settings
        self.processed_ids = set()

    def check(self):
        contacts = load_contacts()

        addresses = [
            contact.email
            for contact in contacts
        ]

        incoming = read_new_messages(
            self.settings,
            addresses
        )

        new_messages = []

        for message in incoming:
            if message["id"] in self.processed_ids:
                continue

            contact = next(
                (
                    contact for contact in contacts
                    if normalize_email(contact.email) == normalize_email(message["sender"])
                ),
                None
            )

            if contact is None:
                continue

            save_message(
                contact.email,
                contact.name,
                message["text"]
            )

            self.processed_ids.add(message["id"])
            new_messages.append(message)

        return new_messages
