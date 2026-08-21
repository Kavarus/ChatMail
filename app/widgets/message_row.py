"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from datetime import datetime
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout


def format_message_datetime(value):
    if not value:
        return ""

    try:
        message_datetime = datetime.fromisoformat(value)
        return message_datetime.astimezone().strftime("%d.%m %H:%M")
    except (TypeError, ValueError):
        return ""


class MessageRow(BoxLayout):
    message = StringProperty("")
    direction = StringProperty("in")
    created_at = StringProperty("")
    is_my_message = BooleanProperty(False)

    def __init__(self, message, direction, created_at="", **kwargs):
        super().__init__(**kwargs)

        self.direction = direction
        self.message = message
        self.created_at = format_message_datetime(created_at)
        self.is_my_message = direction == "out"

        self.orientation = "horizontal"
        self.size_hint_y = None
