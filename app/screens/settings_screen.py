"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty

from app.services.storage import save_settings
from app.services.storage import load_settings

from app.services.mail_providers import MAIL_PROVIDERS


class SettingsScreen(Screen):
    def on_pre_enter(self):
        settings = load_settings()

        self.ids.provider_spinner.text = settings.get("provider", "Mail.ru")
        self.ids.email_input.text = settings.get("user", "")
        self.ids.password_input.text = settings.get("password", "")
        print("загружены параметры")

    selected_server = StringProperty("Mail.ru")

    def save(self):
        provider = self.ids.provider_spinner.text
        email_address = self.ids.email_input.text.strip()
        password = self.ids.password_input.text.strip()

        if provider not in MAIL_PROVIDERS:
            self.ids.status_label.text = "Выберите почтовый сервис"
            return

        if not email_address or not password:
            self.ids.status_label.text = (
                "Введите адрес и пароль приложения"
            )
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

        save_settings(settings)
        self.manager.transition.direction = "left"
        self.manager.current = "main"

    def go_back(self):
        self.manager.transition.direction = "left"
        self.manager.current = "main"


