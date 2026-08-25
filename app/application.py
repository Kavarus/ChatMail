"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from threading import Lock, Thread
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.lang import Builder
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager

from app.services.logger import logger
from app.services.i18n import i18n
from app.services.app_status import app_status
from app.services.notifications import clear_new_message_marker
from app.screens.main_screen import MainScreen
from app.screens.settings_screen import SettingsScreen
from app.screens.chat_screen import ChatScreen
from app.screens.add_contact_screen import AddContactScreen
from app.screens.edit_contact_screen import EditContactScreen
from app.screens.welcome_screen import WelcomeScreen
from app.services.mail_poller import MailPoller
from app.services.storage import (
    load_settings, has_mail_settings, is_first_run,
    get_saved_language, get_application_settings
)


class ChatApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.mail_check_lock = Lock()
        self.mail_check_running = False
        self.mail_poller = None
        self.mail_check_event = None
        self.mail_check_interval = None
        self.is_app_in_background = False
        self.background_service = None

    def build(self):
        logger.info("Started build()")

        try:
            settings = load_settings()
            i18n.set_language(get_saved_language(settings))

            Builder.load_file("app/kv/welcome_screen.kv")
            Builder.load_file("app/kv/main_screen.kv")
            Builder.load_file("app/kv/settings_screen.kv")
            Builder.load_file("app/kv/message_row.kv")
            Builder.load_file("app/kv/chat_screen.kv")
            Builder.load_file("app/kv/add_contact_screen.kv")
            Builder.load_file("app/kv/edit_contact_screen.kv")
            Builder.load_file("app/kv/contact_row.kv")
            logger.info("KV-files loaded")

            manager = ScreenManager()

            manager.add_widget(WelcomeScreen(name="welcome"))
            manager.add_widget(MainScreen(name="main"))
            manager.add_widget(SettingsScreen(name="settings"))
            manager.add_widget(ChatScreen(name="chat"))
            manager.add_widget(AddContactScreen(name="add_contact"))
            manager.add_widget(EditContactScreen(name="edit_contact"))

            self.mail_poller = None
            self.mail_check_event = None

            if is_first_run(settings):
                manager.current = "welcome"
                logger.info("First launch: welcome screen shown")
            else:
                manager.current = "main"
                self.initialize_mail_check(settings)

            return manager
        except Exception:
            logger.exception("Error on manager create")
            raise

    def get_mail_intervals(self):
        settings = load_settings()
        application = get_application_settings(settings)

        return (
            int(application["active_mail_interval"]),
            int(application["background_mail_interval"]),
        )

    def initialize_mail_check(self, settings):
        if not has_mail_settings(settings):
            app_status.set("Ошибка проверки почты: не настроено подключение", level="error")
            return

        self.mail_poller = MailPoller(settings)
        active_interval, _ = self.get_mail_intervals()
        self.schedule_mail_check(active_interval)

    def on_start(self):
        logger.info("Application started")
        clear_new_message_marker()
        settings = load_settings()
        if has_mail_settings(settings):
            logger.info("Mail settings exist; starting background service")
            self.start_background_service()
        else:
            logger.warning("Background service is not started: mail settings are incomplete")

    def on_pause(self):
        logger.info("Application paused")
        self.is_app_in_background = True
        _, background_interval = self.get_mail_intervals()
        self.schedule_mail_check(background_interval)
        return True

    def on_resume(self):
        logger.info("Application resumed")
        self.is_app_in_background = False

        if self.mail_poller is not None:
            active_interval, _ = self.get_mail_intervals()
            self.schedule_mail_check(active_interval)

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

    def open_main_screen(self):
        logger.info("Opening main screen")
        try:
            settings = load_settings()
            self.root.transition.direction = "left"
            self.root.current = "main"
            logger.info("Main screen opened")
            self.initialize_mail_check(settings)
        except Exception as error:
            logger.exception(f"Failed to open main screen: {error}")

    def enable_mail_check(self, settings):
        if self.mail_check_event is not None:
            self.mail_check_event.cancel()

        self.mail_poller = MailPoller(settings)
        active_interval, _ = self.get_mail_intervals()
        self.schedule_mail_check(active_interval)
        logger.info("Mail checking enabled")

    def start_mail_check(self, dt):
        app_status.set("Проверка почты...", level="info")

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
        if messages:
            app_status.set(f"Получено новых сообщений: {len(messages)}", level="success")
        else:
            app_status.set("Новых сообщений нет", level="info")
        for message in messages:
            self.process_incoming_message(message)

    @mainthread
    def on_mail_check_error(self, error):
        app_status.set(f"Mail check error: {error}", level="error")

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
            app_status.set("MailPoller not initiated", level="error")
            return

        self.mail_check_event = Clock.schedule_interval(
            self.start_mail_check,
            interval,
        )
        app_status.set(f"Mail checking scheduled every {interval} seconds", level="info")

    def start_background_service(self):
        if platform != "android":
            logger.info(f"Background service is not started: platform={platform}")
            return

        if self.background_service is not None:
            logger.info("Background service is already started")
            return

        try:
            logger.info("Starting Android background service")

            from android import AndroidService  # type: ignore

            self.background_service = AndroidService("ChatMail", "Проверка почты выполняется в фоне")
            self.background_service.start("service/main.py")
            logger.info("Android background service start requested")

        except Exception as error:
            logger.exception(f"Cannot start Android background service: {error}")
