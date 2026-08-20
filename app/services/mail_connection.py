"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

import imaplib
import smtplib


def check_mail_connection(settings):
    """
    Проверяет подключение и авторизацию через IMAP и SMTP.
    При ошибке выбрасывает исключение.
    """

    imap = None
    smtp = None

    try:
        # Проверка IMAP
        imap = imaplib.IMAP4_SSL(
            settings["imap_server"],
            int(settings.get("imap_port", 993)),
            timeout=15,
        )
        imap.login(
            settings["user"],
            settings["password"],
        )
        imap.logout()
        imap = None

        # Проверка SMTP
        smtp_server = settings["smtp_server"]
        smtp_port = int(settings.get("smtp_port", 465))

        if settings.get("ssl", True):
            smtp = smtplib.SMTP_SSL(
                smtp_server,
                smtp_port,
                timeout=15,
            )
        else:
            smtp = smtplib.SMTP(
                smtp_server,
                smtp_port,
                timeout=15,
            )
            smtp.starttls()

        smtp.login(
            settings["user"],
            settings["password"],
        )

    finally:
        if imap is not None:
            try:
                imap.logout()
            except Exception:
                pass

        if smtp is not None:
            try:
                smtp.quit()
            except Exception:
                pass
