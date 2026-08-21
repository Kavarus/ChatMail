"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout


class ContactRow(BoxLayout):
    contact = ObjectProperty(None, allownone=True)

    def __init__(self, contact, **kwargs):
        super().__init__(**kwargs)

        self.contact = contact
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = "60dp"
        self.register_event_type("on_chat_release")
        self.register_event_type("on_edit_release")

    def on_chat_release(self):
        pass

    def on_edit_release(self):
        pass
