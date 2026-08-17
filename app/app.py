"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from threading import Lock, Thread
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

from app.screens.main_screen import MainScreen
from app.screens.settings_screen import SettingsScreen
from app.screens.chat_screen import ChatScreen
from app.screens.add_contact_screen import AddContactScreen
from app.services.mail_poller import MailPoller
from app.services.storage import load_settings
from app.services.contacts import load_contacts


class ChatApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.mail_check_lock = Lock()
        self.mail_check_running = False
        self.mail_check_event = None

    def build(self):
        settings = load_settings()
        contacts = load_contacts()

        Builder.load_file("app/kv/main_screen.kv")
        Builder.load_file("app/kv/settings_screen.kv")
        Builder.load_file("app/kv/message_row.kv")
        Builder.load_file("app/kv/chat_screen.kv")
        Builder.load_file("app/kv/add_contact_screen.kv")

        manager = ScreenManager()

        manager.add_widget(MainScreen(name="main"))
        manager.add_widget(SettingsScreen(name="settings"))
        manager.add_widget(ChatScreen(name="chat"))
        manager.add_widget(AddContactScreen(name="add_contact"))

        self.mail_poller = MailPoller(settings)

        self.mail_check_event = Clock.schedule_interval(
            self.start_mail_check,
            10
        )

        return manager

    def start_mail_check(self, dt):
        with self.mail_check_lock:
            if self.mail_check_running:
                return

            self.mail_check_running = True

        worker = Thread(
            target=self.mail_check_worker,
            daemon=True
        )
        worker.start()

    def mail_check_worker(self):
        try:
            messages = self.mail_poller.check()

        except Exception as error:
            self.on_mail_check_error(error)

        else:
            self.on_mail_check_success(messages)

        finally:
            with self.mail_check_lock:
                self.mail_check_running = False

    @mainthread
    def on_mail_check_success(self, messages):
        for message in messages:
            self.process_incoming_message(message)

    @mainthread
    def on_mail_check_error(self, error):
        print("Ошибка проверки почты:", error)

    def process_incoming_message(self, message):
        screen = self.root.current_screen

        # Обновляем список контактов в основном окне
        if hasattr(screen, "update_contact"):
            screen.update_contact(message)

        # Обновляем открытый чат
        if screen.name == "chat":
            if (
                    screen.contact_address.lower()
                    == message["sender"].lower()
            ):
                screen.add_received_message(message)

    def on_stop(self):
        # Останавливаем таймер перед завершением приложения.
        if self.mail_check_event is not None:
            self.mail_check_event.cancel()
