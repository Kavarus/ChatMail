"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

import imaplib
import email
from email.utils import parseaddr
from email.header import decode_header, make_header

from app.services.logger import logger


def get_body(message):
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                data = part.get_payload(decode=True)
                if data:
                    return data.decode(
                        part.get_content_charset() or "utf-8",
                        errors="replace"
                    )
        return ""

    data = message.get_payload(decode=True)
    return data.decode(
        message.get_content_charset() or "utf-8",
        errors="replace"
    ) if data else ""


def decode_header_text(value):
    if not value:
        return ""

    try:
        return str(make_header(decode_header(value)))
    except Exception:
        return str(value)


def read_new_messages(settings, contact_addresses):
    logger.info("Mail reading. Contacts: %d", len(contact_addresses))

    messages = []

    server = settings["imap_server"]
    port = int(settings.get("imap_port", 993))

    try:
        mailbox = imaplib.IMAP4_SSL(
            server,
            port,
            timeout=10
        )

        mailbox.login(settings["user"], settings["password"])
        logger.info("IMAP-server authority success")
        mailbox.select("INBOX")

        status, data = mailbox.search(None, "UNSEEN")
        if status != "OK":
            return messages

        addresses = {
            address.lower()
            for address in contact_addresses
        }

        message_ids = data[0].split()

        for message_id in message_ids:
            status, raw_data = mailbox.fetch(
                message_id,
                "(RFC822)"
            )

            if status != "OK":
                continue

            message = email.message_from_bytes(raw_data[0][1])
            _, sender = parseaddr(message.get("From", ""))
            sender = sender.lower()

            if sender not in addresses:
                continue

            messages.append({
                "id": message_id.decode(),
                "sender": sender,
                "subject": decode_header_text(message.get("Subject", "")),
                "text": get_body(message),
            })

        return messages

    except Exception:
        logger.exception("IMAP-server authority error (%s:%d)", server, port)
        raise
