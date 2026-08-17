"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from kivy.properties import StringProperty
from kivy.uix.button import Button


class ContactRow(Button):
    name = StringProperty("")
    address = StringProperty("")

    def __init__(self, contact, **kwargs):
        super().__init__(**kwargs)

        self.contact = contact
        self.name = contact.name
        self.address = contact.email

        self.text = f"{contact.name}\n{contact.email}"
        self.size_hint_y = None
        self.height = "60dp"
