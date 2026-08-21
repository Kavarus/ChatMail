"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from threading import Thread
from kivy.app import App
from kivy.clock import mainthread
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty

from app.services.logger import logger
from app.services.storage import save_settings, load_settings
from app.data.mail_providers import MAIL_PROVIDERS
from app.services.mail_connection import check_mail_connection


class SettingsScreen(Screen):
    def on_pre_enter(self):
        settings = load_settings()

        self.ids.provider_spinner.text = settings.get("provider", "Mail.ru")
        self.ids.email_input.text = settings.get("user", "")
        self.ids.password_input.text = settings.get("password", "")
        self.clear_status()
        logger.info("Settings loaded")

    selected_server = StringProperty("Mail.ru")

    def clear_status(self):
        self.ids.status_label.text = ""
        self.ids.status_label.color = (0.3, 0.7, 0.3, 1)

    def show_status(self, message):
        self.ids.status_label.color = (0.2, 0.7, 0.2, 1)
        self.ids.status_label.text = message

    def show_error(self, message):
        self.ids.status_label.color = (0.9, 0.2, 0.2, 1)
        self.ids.status_label.text = message

    def save(self):
        provider = self.ids.provider_spinner.text
        email_address = self.ids.email_input.text.strip()
        password = self.ids.password_input.text.strip()
        self.clear_status()

        if provider not in MAIL_PROVIDERS:
            self.show_error("Не выбран почтовый сервис")
            return

        if not email_address:
            self.show_error("Не заполнен адрес")
            return

        if not password:
            self.show_error("Не заполнен пароль")
            return

        provider_settings = MAIL_PROVIDERS[provider]

        settings = {
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
            target=self._check_and_save,
            args=(settings,),
            daemon=True,
        ).start()

    def _check_and_save(self, settings):
        """
        Сначала проверяет подключение, затем сохраняет настройки.
        """

        try:
            check_mail_connection(settings)
            save_settings(settings)
            App.get_running_app().enable_mail_check(settings)

        except Exception as error:
            self.on_save_error(error)
            return

        self.on_save_success()

    @mainthread
    def on_save_success(self):
        self.set_saving_state(False)
        logger.info("New settings saved")
        self.show_status("Настройки успешно сохранены")

    @mainthread
    def on_save_error(self, error):
        self.set_saving_state(False)
        logger.exception(f"Mail connection check error: {error}")
        self.show_error("Ошибка подключения, настройки не сохранены")

    @mainthread
    def set_saving_state(self, saving):
        self.ids.save_button.disabled = saving

        if saving:
            self.ids.save_button.text = "Проверка..."
        else:
            self.ids.save_button.text = "Сохранить"

    def go_back(self):
        self.manager.transition.direction = "left"
        self.manager.current = "main"
