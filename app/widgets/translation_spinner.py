"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from kivy.properties import ListProperty, StringProperty
from kivy.uix.spinner import Spinner
from app.services.i18n import i18n


class TranslationSpinner(Spinner):
    language_items = ListProperty([])
    selected_language = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_languages()
        i18n.bind(on_language_changed=self._on_language_changed)
        self.bind(text=self._on_text_changed)

    def update_languages(self):
        self.language_items = i18n.get_language_items()
        self.values = [language_name for language_name, language_code in self.language_items]
        self.text = i18n.get_language_name(i18n.language)
        self.selected_language = i18n.language

    def _on_language_changed(self, *_):
        self.update_languages()

    def _on_text_changed(self, *_):
        for language_name, language_code in self.language_items:
            if language_name == self.text:
                self.selected_language = language_code
                break
