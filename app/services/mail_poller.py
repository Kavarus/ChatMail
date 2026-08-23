"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from app.services.logger import logger
from app.services.mail_reader import read_new_messages
from app.services.chat_storage import save_message
from app.services.contacts import load_contacts
from app.services.storage import (load_processed_ids, save_processed_ids, get_connection_settings)


def normalize_email(value: str) -> str:
    return value.strip().lower()


class MailPoller:
    def __init__(self, settings):
        self.settings = get_connection_settings(settings)
        self.processed_ids = load_processed_ids()
        logger.info("MailPoller initialize")

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
        logger.info("Get incoming messages by IMAP: %d", len(incoming))

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

            try:
                save_message(
                    contact_guid=contact.guid,
                    direction="in",
                    text=message["text"],
                    created_at=message["created_at"],
                )
            except Exception as error:
                unsaved_message = message["id"]
                logger.exception(f"Failed to save incoming message {unsaved_message}: {error}")
                continue

            contact.has_new_messages = True
            message["contact_guid"] = contact.guid
            message["contact_name"] = contact.name

            self.processed_ids.add(message["id"])
            new_messages.append(message)

        # Сохраняем флаги новых сообщений
        from app.services.contacts import save_contacts
        save_contacts(contacts)

        if new_messages:
            save_processed_ids(self.processed_ids)
            logger.info("New messages from contacts: %d", len(new_messages))

        return new_messages
