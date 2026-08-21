"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

import imaplib
import email
from datetime import datetime, timezone
from email.utils import parseaddr, parsedate_to_datetime
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


def get_message_datetime(message):
    value = message.get("Date", "")

    if value:
        try:
            message_datetime = parsedate_to_datetime(value)

            if message_datetime.tzinfo is None:
                message_datetime = message_datetime.replace(
                    tzinfo=timezone.utc
                )

            return message_datetime.astimezone(
                timezone.utc
            ).isoformat()

        except (TypeError, ValueError, IndexError):
            pass

    return datetime.now(timezone.utc).isoformat()


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
            status, raw_data = mailbox.fetch(message_id, "(BODY.PEEK[])")

            if status != "OK":
                continue

            message = email.message_from_bytes(raw_data[0][1])
            subject = decode_header_text(message.get("Subject", "")).strip()

            if subject != "ChatMail message":
                continue

            _, sender = parseaddr(message.get("From", ""))
            sender = sender.lower()

            if sender not in addresses:
                continue

            messages.append({
                "id": message_id.decode(),
                "sender": sender,
                "subject": subject,
                "text": get_body(message),
                "created_at": get_message_datetime(message),
            })
            mark_as_seen(mailbox, message_id)

        return messages

    except Exception:
        logger.exception("IMAP-server authority error (%s:%d)", server, port)
        raise

    finally:
        if mailbox is not None:
            try:
                mailbox.logout()
            except Exception:
                pass


def mark_as_seen(mailbox, message_id):
    status, _ = mailbox.store(message_id, "+FLAGS", r"(\Seen)")
    if status != "OK":
        raise RuntimeError(f"Не удалось пометить письмо {message_id} как прочитанное")
