"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from kivy.uix.screenmanager import Screen
from app.services.logger import logger
from app.services.contacts import load_contacts, mark_contact_as_read
from app.widgets.contact_row import ContactRow
from app.services.app_status import app_status


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
        logger.info("Loading contacts")
        try:
            contacts_box = self.ids.contacts_list
            contacts_box.clear_widgets()

            contacts = load_contacts()
            for contact in contacts:
                row = ContactRow(contact=contact)
                row.bind(on_chat_release=self.open_chat)
                row.bind(on_edit_release=self.open_edit_contact)
                contacts_box.add_widget(row)
            logger.info(f"Contacts loaded: {len(contacts)}")

        except Exception as error:
            app_status.set(f"Ошибка загрузки контактов: {error}", level="error")

    def open_chat(self, row):
        """Открыть чат с выбранным контактом."""
        mark_contact_as_read(row.contact.guid)
        chat_screen = self.manager.get_screen("chat")
        chat_screen.set_contact(row.contact)

        self.manager.transition.direction = "left"
        self.manager.current = "chat"

    def open_edit_contact(self, row):
        edit_screen = self.manager.get_screen("edit_contact")
        edit_screen.set_contact(row.contact)

        self.manager.transition.direction = "left"
        self.manager.current = "edit_contact"
