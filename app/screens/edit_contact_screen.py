"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from kivy.uix.screenmanager import Screen
from app.services.contacts import update_contact


class EditContactScreen(Screen):
    contact = None

    def set_contact(self, contact):
        self.contact = contact

        self.ids.contact_name.text = contact.name
        self.ids.contact_address.text = contact.email
        self.ids.error_label.text = ""

    def save_contact(self):
        name = self.ids.contact_name.text.strip()
        address = self.ids.contact_address.text.strip()

        if not name or not address:
            self.ids.error_label.text = (
                "Заполните имя и почту"
            )
            return

        try:
            update_contact(
                guid=self.contact.guid,
                name=name,
                address=address,
            )

        except ValueError as error:
            self.ids.error_label.text = str(error)
            return

        self.manager.transition.direction = "right"
        self.manager.current = "main"

    def cancel(self):
        self.manager.transition.direction = "right"
        self.manager.current = "main"
