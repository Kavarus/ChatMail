"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

import smtplib
from email.message import EmailMessage
from app.services.logger import logger
from app.services.storage import load_settings


def send_email(recipient, subject, body):
    logger.info("Email send starting. Address: %s", recipient)

    settings = load_settings()

    server = settings.get("smtp_server")
    username = settings.get("user")
    password = settings.get("password")

    if not server or not username or not password:
        logger.error("SMTP-settings not found")
        raise ValueError("Не заполнены настройки почтового сервера")

    try:
        message = EmailMessage()
        message["From"] = username
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)

        # Обычно SMTP-серверы используют порт 465 с SSL. (server, 465, timeout=20)
        port = int(settings.get("smtp_port", 465))

        with smtplib.SMTP_SSL(server, port, timeout=20) as smtp:
            logger.info("Connection to SMTP-server %s success", server)
            smtp.login(username, password)
            logger.info("SMTP-server authority success")
            smtp.send_message(message)
            logger.info("Message send success")

    except Exception:
        logger.exception("Message send failed. Address: %s", recipient)
        raise
