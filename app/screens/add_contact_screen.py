"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from kivy.uix.screenmanager import Screen

from app.services.contacts import add_contact


class AddContactScreen(Screen):
    parent_screen = None

    def set_parent(self, parent_screen):
        self.parent_screen = parent_screen
        self.ids.contact_name.text = ""
        self.ids.contact_address.text = ""

    def save_contact(self):
        name = self.ids.contact_name.text.strip()
        address = self.ids.contact_address.text.strip()

        if not name or not address:
            self.ids.error_label.text = "Заполните оба поля"
            return

        add_contact(name, address)

        self.parent_screen.load_contact_list()

        self.manager.transition.direction = "right"
        self.manager.current = "main"

    def cancel(self):
        self.manager.transition.direction = "right"
        self.manager.current = "main"