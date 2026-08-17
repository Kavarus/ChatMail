"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout

from app.services.contacts import load_contacts
from app.widgets.contact_row import ContactRow


class MainScreen(Screen):

    def on_enter(self):
        """Вызывается при открытии основного экрана."""
        self.load_contact_list()

    def open_settings(self):
        """Открыть экран настроек."""
        self.manager.transition.direction = "right"
        self.manager.current = "settings"

    def add_contact(self):
        """Открыть форму добавления контакта."""
        self.manager.get_screen("add_contact").set_parent(self)
        self.manager.transition.direction = "left"
        self.manager.current = "add_contact"

    def load_contact_list(self):
        """Считать контакты и показать их на экране."""
        contacts_box = self.ids.contacts_list
        contacts_box.clear_widgets()

        contacts = load_contacts()

        for contact in contacts:
            row = ContactRow(contact)
            row.bind(on_release=self.open_chat)
            contacts_box.add_widget(row)

    def open_chat(self, row):
        """Открыть чат с выбранным контактом."""
        chat_screen = self.manager.get_screen("chat")

        chat_screen.set_contact(
            name=row.contact.name,
            address=row.contact.email
        )

        self.manager.transition.direction = "left"
        self.manager.current = "chat"
