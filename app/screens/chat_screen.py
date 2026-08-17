"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from threading import Thread

from kivy.clock import mainthread
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen

from app.services.mail_sender import send_email
from app.widgets.message_row import MessageRow
from app.services.chat_storage import (
    load_messages,
    save_message
)


class ChatScreen(Screen):
    contact_name = StringProperty("")
    contact_address = StringProperty("")

    def add_received_message(self, message):
        row = MessageRow(
            sender=message["sender"],
            message=message["text"]
        )

        self.ids.messages_list.add_widget(row)

    def set_contact(self, name, address):
        """Установить выбранного собеседника."""
        self.contact_name = name
        self.contact_address = address
        self.load_messages()

    def load_messages(self):
        """Загрузить сообщения чата."""
        messages_box = self.ids.messages_list
        messages_box.clear_widgets()

        messages = load_messages(self.contact_address)

        for message in messages:
            row = MessageRow(
                sender=message["sender"],
                message=message["text"]
            )
            messages_box.add_widget(row)

    def send_message(self):
        """Отправить сообщение."""
        text = self.ids.message_input.text.strip()

        # Пустое сообщение не отправляем
        if not text:
            return

        if not self.contact_address:
            self.show_status("Не выбран получатель")
            return

        # Сохраняем текст до очистки поля
        self.ids.message_input.text = ""
        self.show_status("Отправка...")

        # Отправка в отдельном потоке, чтобы не блокировать интерфейс
        Thread(
            target=self._send_email_in_background,
            args=(self.contact_address, text),
            daemon=True
        ).start()

    def _send_email_in_background(self, recipient, text):
        try:
            send_email(
                recipient=recipient,
                subject="ChatMail message",
                body=text
            )
        except Exception as error:
            self.show_status(f"Ошибка отправки: {error}")
            return

        self.add_sent_message(
            recipient,
            text
        )
        self.show_status("Сообщение отправлено")

    @mainthread
    def add_sent_message(self, recipient, text):
        save_message(
            contact_address=recipient,
            sender="me",
            text=text
        )

        # Показываем сообщение только если пользователь
        # все еще находится в том же чате
        if self.contact_address.lower() != recipient.lower():
            return

        row = MessageRow(
            sender="me",
            message=text
        )

        self.ids.messages_list.add_widget(row)

    @mainthread
    def show_status(self, text):
        self.ids.status_label.text = text

    def go_back(self):
        """Вернуться к списку контактов."""
        self.manager.transition.direction = "right"
        self.manager.current = "main"
