"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

import json
import smtplib
from email.message import EmailMessage
from pathlib import Path


SETTINGS_FILE = Path("data/settings.json")


def load_settings():
    if not SETTINGS_FILE.exists():
        raise FileNotFoundError("Файл настроек не найден")

    with SETTINGS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def send_email(recipient, subject, body):
    settings = load_settings()

    server = settings.get("smtp_server")
    username = settings.get("user")
    password = settings.get("password")

    if not server or not username or not password:
        raise ValueError("Не заполнены настройки почтового сервера")

    message = EmailMessage()
    message["From"] = username
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    # Обычно SMTP-серверы используют порт 465 с SSL. (server, 465, timeout=20)
    port = int(settings.get("smtp_port", 465))

    with smtplib.SMTP_SSL(server, port, timeout=20) as smtp:
        smtp.login(username, password)
        smtp.send_message(message)
