"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from threading import Thread
from datetime import datetime, timezone
from kivy.clock import mainthread
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen

from app.services.logger import logger
from app.services.mail_sender import send_email
from app.widgets.message_row import MessageRow
from app.services.chat_storage import (
    load_messages,
    save_message
)


def parse_message_datetime(message):
    value = message.get("created_at")

    if not value:
        return datetime.min.replace(tzinfo=timezone.utc)

    try:
        result = datetime.fromisoformat(value)
        if result.tzinfo is None:
            result = result.replace(tzinfo=timezone.utc)
        return result.astimezone(timezone.utc)

    except (TypeError, ValueError):
        return datetime.min.replace(tzinfo=timezone.utc)


class ChatScreen(Screen):
    contact_name = StringProperty("")
    contact_address = StringProperty("")
    contact_guid = StringProperty("")

    def set_contact(self, contact):
        """Установить выбранного собеседника."""
        self.contact_name = contact.name
        self.contact_address = contact.email
        self.contact_guid = contact.guid
        self.load_messages()

    def load_messages(self):
        """Загрузить сообщения чата."""
        messages_box = self.ids.messages_list
        messages_box.clear_widgets()

        messages = load_messages(self.contact_guid)
        messages.sort(key=parse_message_datetime)

        for message in messages:
            row = MessageRow(
                message=message.get("text", ""),
                direction=message.get("direction", "in"),
                created_at=message.get("created_at", ""),
            )
            messages_box.add_widget(row)

    def send_message(self):
        text = self.ids.message_input.text.strip()

        # Пустое сообщение не отправляем
        if not text:
            return

        logger.info("Send message from chat screen")

        if not self.contact_address:
            logger.warning("Contact address not found")
            self.show_status("Не указан получатель")
            return

        # Сохраняем текст до очистки поля
        self.ids.message_input.text = ""
        self.show_status("Отправка...")

        # Отправка в отдельном потоке, чтобы не блокировать интерфейс
        Thread(
            target=self._send_email_in_background,
            args=(self.contact_address, self.contact_guid, text),
            daemon=True
        ).start()

    def _send_email_in_background(self, recipient, contact_guid, text):
        logger.info("Email send in background started")
        created_at = datetime.now(timezone.utc).isoformat()
        try:
            send_email(
                recipient=recipient,
                subject="ChatMail message",
                body=text
            )
            save_message(
                contact_guid=contact_guid,
                direction="out",
                text=text,
                created_at=created_at,
            )

        except Exception as error:
            logger.exception("Email send failed. %s", error)
            self.show_status(f"Ошибка отправки: {error}")
            return

        self.add_sent_message(text, created_at)
        logger.info("Email send in background ended")
        self.show_status("Сообщение отправлено")

    @mainthread
    def add_received_message(self, message):
        if message["contact_guid"] != self.contact_guid:
            return

        row = MessageRow(
            message=message["text"],
            direction="in",
            created_at=message["created_at"],
        )

        self.ids.messages_list.add_widget(row)

    @mainthread
    def add_sent_message(self, text, created_at):
        row = MessageRow(
            message=text,
            direction="out",
            created_at=created_at,
        )
        self.ids.messages_list.add_widget(row)

    @mainthread
    def show_status(self, text):
        self.ids.status_label.text = text

    def go_back(self):
        """Вернуться к списку контактов."""
        self.manager.transition.direction = "right"
        self.manager.current = "main"
