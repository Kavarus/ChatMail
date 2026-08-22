"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from kivy.properties import StringProperty
from kivy.uix.label import Label
from app.services.i18n import i18n


class TranslationLabel(Label):
    translation_key = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(translation_key=self._on_translation_key)
        i18n.bind(on_language_changed=self._on_language_changed)

    def _on_translation_key(self, *_):
        self.update_translation()

    def _on_language_changed(self, *_):
        self.update_translation()

    def update_translation(self, *_):
        self.text = i18n.get(self.translation_key)
        self.texture_update()
