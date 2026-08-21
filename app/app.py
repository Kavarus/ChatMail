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

from app.services.logger import logger
from app.screens.main_screen import MainScreen
from app.screens.settings_screen import SettingsScreen
from app.screens.chat_screen import ChatScreen
from app.screens.add_contact_screen import AddContactScreen
from app.screens.edit_contact_screen import EditContactScreen
from app.services.mail_poller import MailPoller
from app.services.storage import load_settings, has_mail_settings

ACTIVE_MAIL_INTERVAL = 45
BACKGROUND_MAIL_INTERVAL = 300


class ChatApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.mail_check_lock = Lock()
        self.mail_check_running = False
        self.mail_poller = None
        self.mail_check_event = None
        self.mail_check_interval = None
        self.is_app_in_background = False

    def build(self):
        logger.info("Started build()")

        try:
            settings = load_settings()

            Builder.load_file("app/kv/main_screen.kv")
            Builder.load_file("app/kv/settings_screen.kv")
            Builder.load_file("app/kv/message_row.kv")
            Builder.load_file("app/kv/chat_screen.kv")
            Builder.load_file("app/kv/add_contact_screen.kv")
            Builder.load_file("app/kv/edit_contact_screen.kv")
            Builder.load_file("app/kv/contact_row.kv")
            logger.info("KV-files loaded")

            manager = ScreenManager()

            manager.add_widget(MainScreen(name="main"))
            manager.add_widget(SettingsScreen(name="settings"))
            manager.add_widget(ChatScreen(name="chat"))
            manager.add_widget(AddContactScreen(name="add_contact"))
            manager.add_widget(EditContactScreen(name="edit_contact"))

            self.mail_poller = None
            self.mail_check_event = None

            if has_mail_settings(settings):
                self.mail_poller = MailPoller(settings)
                self.schedule_mail_check(ACTIVE_MAIL_INTERVAL)
            else:
                logger.info("Mail checking is disabled: settings are empty")

            return manager
        except Exception:
            logger.exception("Error on manager create")
            raise

    def on_start(self):
        logger.info("Application started")

    def on_pause(self):
        logger.info("Application paused")
        self.is_app_in_background = True
        self.schedule_mail_check(BACKGROUND_MAIL_INTERVAL)
        return True

    def on_resume(self):
        logger.info("Application resumed")
        self.is_app_in_background = False

        if self.mail_poller is not None:
            self.schedule_mail_check(ACTIVE_MAIL_INTERVAL)

            # Желательно проверить почту сразу после возвращения
            Clock.schedule_once(
                lambda dt: self.start_mail_check(dt),
                0,
            )

    def on_stop(self):
        # Останавливаем таймер перед завершением приложения.
        if self.mail_check_event is not None:
            self.mail_check_event.cancel()
        logger.info("Application stopped")

    def enable_mail_check(self, settings):
        if self.mail_check_event is not None:
            self.mail_check_event.cancel()

        self.mail_poller = MailPoller(settings)
        self.schedule_mail_check(ACTIVE_MAIL_INTERVAL)
        logger.info("Mail checking enabled")

    def start_mail_check(self, dt):
        logger.debug("Mail check started")

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
            logger.info("Mail checked. New messages: %d", len(messages))

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
        logger.exception(f"Mail check error: {error}")

    def process_incoming_message(self, message):
        logger.info("Incoming message processing begin")
        contact_guid = message["contact_guid"]

        main_screen = self.root.get_screen("main")
        main_screen.load_contact_list()
        chat_screen = self.root.get_screen("chat")

        # Обновляем открытый чат
        if self.root.current == "chat" and chat_screen.contact_guid == contact_guid:
            chat_screen.add_received_message(message)

    def schedule_mail_check(self, interval):
        if self.mail_check_event is not None:
            self.mail_check_event.cancel()
            self.mail_check_event = None

        self.mail_check_interval = interval

        if self.mail_poller is None:
            logger.debug("MailPoller not initiated. Mail checking schedule not started.")
            return

        self.mail_check_event = Clock.schedule_interval(
            self.start_mail_check,
            interval,
        )
        logger.info("Mail checking scheduled every %s seconds", interval)
