"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from kivy.clock import mainthread
from kivy.properties import ListProperty
from kivy.uix.label import Label

from app.services.app_status import app_status


class AppStatusLabel(Label):
    status_color = ListProperty((0.35, 0.35, 0.35, 1))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        app_status.bind(
            text=self._on_status_text,
            level=self._on_status_level,
        )

        self.text = app_status.text
        self.update_color(app_status.level)

    @mainthread
    def _on_status_text(self, instance, value):
        self.text = value

    @mainthread
    def _on_status_level(self, instance, value):
        self.update_color(value)

    def update_color(self, level):
        colors = {
            "info": (0.35, 0.35, 0.35, 1),
            "success": (0.15, 0.60, 0.20, 1),
            "warning": (0.85, 0.55, 0.05, 1),
            "error": (0.90, 0.15, 0.15, 1),
        }

        self.status_color = colors.get(level,  colors["info"])
