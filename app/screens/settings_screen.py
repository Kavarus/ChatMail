"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from threading import Thread
from kivy.app import App
from kivy.clock import mainthread
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

from app.services.logger import logger, LOG_FILE
from app.services.storage import (
    save_settings, load_settings, has_mail_settings,
    get_application_settings, get_connection_settings
)
from app.data.mail_providers import MAIL_PROVIDERS
from app.services.mail_connection import check_mail_connection
from app.services.i18n import i18n
from app.services.mail_sender import send_email

DEVELOPER_EMAIL = "developer@example.com"


class SettingsScreen(Screen):
    settings_mode = StringProperty("application")
    selected_server = StringProperty("Mail.ru")
    has_connection = BooleanProperty(False)
    active_interval = NumericProperty(45)
    background_interval = NumericProperty(300)

    def on_pre_enter(self):
        self.load_form()

    def open_mode(self, mode):
        if mode not in ("application", "connection"):
            mode = "connection"
        self.settings_mode = mode
        self.load_form()

    def load_form(self):
        settings = load_settings()
        application = get_application_settings(settings)
        connection = get_connection_settings(settings)
        self.has_connection = has_mail_settings(settings)

        self.active_interval = self.normalize_active_interval(application.get("active_mail_interval", 45))
        self.background_interval = self.normalize_back_interval(application.get("background_mail_interval", 300))
        self.ids.language_spinner.update_languages()
        i18n.set_language(application["language"])
        self.ids.provider_spinner.text = connection.get("provider", "Mail.ru")
        self.ids.email_input.text = connection.get("user", "")
        self.ids.password_input.text = connection.get("password", "")
        self.clear_status()
        logger.info("Settings loaded")

    def clear_status(self):
        self.ids.status_label.text = ""
        self.ids.status_label.color = (0.3, 0.7, 0.3, 1)

    def show_status(self, message):
        self.ids.status_label.color = (0.2, 0.7, 0.2, 1)
        self.ids.status_label.text = message

    def show_error(self, message):
        self.ids.status_label.color = (0.9, 0.2, 0.2, 1)
        self.ids.status_label.text = message

    def save_current_settings(self):
        if self.settings_mode == "application":
            self.save_application()
        else:
            self.save_connection()

    def save_application(self):
        try:
            active_interval = int(self.active_interval)
            background_interval = int(self.background_interval)
        except ValueError:
            self.show_error(i18n.get("interval_invalid"))
            return

        if active_interval < 1 or background_interval < 1:
            self.show_error(i18n.get("interval_invalid"))
            return

        settings = load_settings()
        settings["application"] = {
            "active_mail_interval": active_interval,
            "background_mail_interval": background_interval,
            "language": self.ids.language_spinner.selected_language,
        }

        save_settings(settings)
        i18n.set_language(settings["application"]["language"])

        app = App.get_running_app()
        if app.mail_poller is not None:
            app.schedule_mail_check(active_interval)

        self.show_status(i18n.get("settings_saved"))

    def save_connection(self):
        provider = self.ids.provider_spinner.text
        email_address = self.ids.email_input.text.strip()
        password = self.ids.password_input.text.strip()

        if provider not in MAIL_PROVIDERS:
            self.show_error(i18n.get("provider_required"))
            return

        if not email_address:
            self.show_error(i18n.get("email_required"))
            return

        if not password:
            self.show_error(i18n.get("password_required"))
            return

        provider_settings = MAIL_PROVIDERS[provider]

        connection = {
            "provider": provider,
            "user": email_address,
            "password": password,
            "smtp_server": provider_settings["smtp_server"],
            "smtp_port": provider_settings["smtp_port"],
            "imap_server": provider_settings["imap_server"],
            "imap_port": provider_settings["imap_port"],
            "ssl": provider_settings["ssl"],
        }

        self.set_saving_state(True)

        Thread(
            target=self._check_and_save_connection,
            args=(connection,),
            daemon=True,
        ).start()

    def _check_and_save_connection(self, connection):
        """
        Сначала проверяет подключение, затем сохраняет настройки.
        """

        try:
            check_mail_connection(connection)
            settings = load_settings()
            settings["connection"] = connection
            save_settings(settings)
            self.on_connection_saved()
            App.get_running_app().enable_mail_check(settings)

        except Exception as error:
            self.on_save_error(error)
            return

        self.on_save_success()

    def open_bug_report(self):
        if not has_mail_settings(load_settings()):
            self.show_error(i18n.get("connection_error"))
            return

        content = BoxLayout(orientation="vertical", spacing="10dp", padding="10dp")
        message_input = TextInput(multiline=True, hint_text=i18n.get("bug_report_hint"), input_type="text")
        buttons = BoxLayout(size_hint_y=None, height="45dp", spacing="10dp")
        popup = Popup(title=i18n.get("bug_report"), content=content, size_hint=(0.9, 0.5), auto_dismiss=False)
        send_button = Button(text=i18n.get("send"))
        cancel_button = Button(text=i18n.get("cancel"))
        send_button.bind(on_release=lambda *_: self.send_bug_report(popup, message_input.text, send_button))
        cancel_button.bind(on_release=lambda *_: popup.dismiss())

        buttons.add_widget(send_button)
        buttons.add_widget(cancel_button)

        content.add_widget(message_input)
        content.add_widget(buttons)

        popup.open()

    def send_bug_report(self, popup, text, button):
        text = text.strip()

        if not text:
            text = i18n.get("default_bug_report")

        button.disabled = True
        button.text = i18n.get("checking")

        Thread(
            target=self._send_bug_report_background,
            args=(popup, text),
            daemon=True,
        ).start()

    def _send_bug_report_background(self, popup, text):
        logger.info(f"Bug report prepared to send")
        try:
            send_email(
                recipient=DEVELOPER_EMAIL,
                subject="ChatMail bug report",
                body=text,
                attachment=LOG_FILE,
            )
        except Exception as error:
            logger.exception(f"Bug report sending failed: {error}")
            self.show_error(i18n.get("bug_report_error").format(error=error))
            return

        popup.dismiss()
        self.show_status(i18n.get("bug_report_sent"))

    def normalize_active_interval(self, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            return 45

        allowed_values = (30, 45, 60, 75, 90)

        return min(allowed_values, key=lambda item: abs(item - value))

    def normalize_back_interval(self, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            return 300

        allowed_values = (180, 240, 300, 360, 420, 480, 540, 600)

        return min(allowed_values, key=lambda item: abs(item - value))

    @mainthread
    def on_save_success(self):
        self.set_saving_state(False)
        logger.info("New settings saved")
        self.show_status(i18n.get("settings_saved"))

    @mainthread
    def on_save_error(self, error):
        self.set_saving_state(False)
        logger.exception(f"Mail connection check error: {error}")
        self.show_error(i18n.get("connection_error"))

    @mainthread
    def on_connection_saved(self):
        self.has_connection = has_mail_settings(load_settings())

    @mainthread
    def set_saving_state(self, saving):
        self.ids.save_button.disabled = saving

        if saving:
            self.ids.save_button.text = i18n.get("checking")
        else:
            self.ids.save_button.text = i18n.get("save")

    def go_back(self):
        self.manager.transition.direction = "left"
        self.manager.current = "main"
