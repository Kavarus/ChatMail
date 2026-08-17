"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout


class MessageRow(BoxLayout):
    sender = StringProperty("")
    message = StringProperty("")
    is_my_message = BooleanProperty(False)

    def __init__(self, sender, message, **kwargs):
        super().__init__(**kwargs)

        self.sender = sender
        self.message = message
        self.is_my_message = sender == "me"

        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = self.minimum_height
