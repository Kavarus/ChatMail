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

MAIL_SUBJECT = "ChatMail message"


def get_body(message):
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                data = part.get_payload(decode=True)
                if data:
                    return data.decode(
                        part.get_content_charset() or "utf-8",
                        errors="replace"
                    ).strip()
        return ""

    data = message.get_payload(decode=True)
    return data.decode(
        message.get_content_charset() or "utf-8",
        errors="replace"
    ).strip() if data else ""


def get_message_datetime(message):
    value = message.get("Date", "")

    if value:
        try:
            message_datetime = parsedate_to_datetime(value)

            if message_datetime.tzinfo is None:
                message_datetime = message_datetime.replace(tzinfo=timezone.utc)

            return message_datetime.astimezone(timezone.utc).isoformat()

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


def read_new_messages(settings, contact_addresses, pending_delete_ids=None):
    logger.info("Mail reading. Contacts: %d", len(contact_addresses))

    messages = []
    mailbox = None
    server = settings["imap_server"]
    port = int(settings.get("imap_port", 993))
    pending_delete_ids = {str(uid) for uid in (pending_delete_ids or set())}

    try:
        mailbox = imaplib.IMAP4_SSL(server, port, timeout=10)
        mailbox.login(settings["user"], settings["password"])
        logger.info("IMAP-server authority success")
        mailbox.select("INBOX")
        deleted_uids = delete_messages_by_uid(mailbox, pending_delete_ids)
        message_ids = search_message_ids(mailbox)
        addresses = {address.strip().lower() for address in contact_addresses}

        for message_id in message_ids:
            uid_text = message_id.decode(errors="replace")
            message = fetch_message(mailbox, message_id)
            if message is None:
                continue

            subject = decode_header_text(message.get("Subject", "")).strip()
            if subject != MAIL_SUBJECT:
                continue

            _, sender = parseaddr(message.get("From", ""))
            sender = sender.strip().lower()

            if sender not in addresses:
                continue

            messages.append({
                "id": uid_text,
                "sender": sender,
                "subject": subject,
                "text": get_body(message),
                "created_at": get_message_datetime(message),
            })
            # mark_as_seen(mailbox, message_id)

        return {"messages": messages, "deleted_ids": deleted_uids}

    except Exception:
        logger.exception("IMAP-server authority error (%s:%d)", server, port)
        raise

    finally:
        if mailbox is not None:
            try:
                mailbox.logout()
            except Exception:
                pass


def search_message_ids(mailbox):
    status, data = mailbox.uid("search", None, "UNSEEN", "SUBJECT", f'"{MAIL_SUBJECT}"')

    if status != "OK":
        raise RuntimeError(f"IMAP search failed: {status}")

    if not data or not data[0]:
        return []

    return data[0].split()


def fetch_message(mailbox, message_uid):
    status, raw_data = mailbox.uid("fetch", message_uid, "(BODY.PEEK[])")

    if status != "OK":
        logger.warning("Cannot fetch message UID %s", message_uid.decode(errors="replace"))
        return None

    raw_message = None

    for item in raw_data:
        if not isinstance(item, tuple):
            continue

        if len(item) < 2:
            continue

        raw_message = item[1]
        break

    if not raw_message:
        logger.warning("Empty message body for UID %s", message_uid.decode(errors="replace"))
        return None

    try:
        return email.message_from_bytes(raw_message)
    except Exception:
        logger.exception("Cannot parse message UID %s", message_uid.decode(errors="replace"))
        return None


def delete_messages_by_uid(mailbox, message_uids):
    deleted_uids = set()

    for uid in message_uids:
        uid = str(uid)
        uid_bytes = uid.encode()

        try:
            status, _ = mailbox.uid("store", uid_bytes, "+FLAGS", r"(\Deleted)")

            if status != "OK":
                logger.warning("Cannot mark UID %s as deleted", uid)
                continue

            deleted_uids.add(uid)
            logger.info("Message UID %s marked for deletion", uid)

        except Exception:
            logger.exception("Cannot mark UID %s for deletion", uid)

    if not deleted_uids:
        return set()

    status, _ = mailbox.expunge()

    if status != "OK":
        logger.warning("IMAP expunge failed: %s", status)
        return set()

    logger.info("Messages permanently deleted: %d", len(deleted_uids))

    return deleted_uids


def mark_as_seen(mailbox, message_id):
    status, _ = mailbox.store(message_id, "+FLAGS", r"(\Seen)")
    if status != "OK":
        raise RuntimeError(f"Не удалось пометить письмо {message_id} как прочитанное")
