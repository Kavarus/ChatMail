"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from kivy.app import App
from kivy.properties import ListProperty
from kivy.uix.screenmanager import Screen

from app.services.i18n import i18n
from app.services.storage import accept_terms


class WelcomeScreen(Screen):
    languages = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        i18n.bind(on_language_changed=self._on_language_changed)

    def on_pre_enter(self):
        self.update_language_spinner()

    def _on_language_changed(self, *_):
        self.update_language_spinner()

    def update_language_spinner(self):
        self.languages = i18n.get_language_items()

        spinner = self.ids.language_spinner
        spinner.update_languages()

    def select_language(self, language):
        if language:
            i18n.set_language(language)

    def accept(self):
        accept_terms(i18n.language)
        app = App.get_running_app()
        app.open_main_screen()
