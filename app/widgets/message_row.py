"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout


class MessageRow(BoxLayout):
    message = StringProperty("")
    direction = StringProperty("in")
    is_my_message = BooleanProperty(False)

    def __init__(self, message, direction, **kwargs):
        super().__init__(**kwargs)

        self.direction = direction
        self.message = message
        self.is_my_message = direction == "out"

        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = self.minimum_height
