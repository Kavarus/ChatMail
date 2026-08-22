"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from app.services.contacts import update_contact, delete_contact
from app.services.chat_storage import delete_messages
from app.services.i18n import i18n


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

    def confirm_delete(self):
        content = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=10,
        )

        content.add_widget(Label(text=i18n.get("delete_confirmation")))

        buttons = BoxLayout(
            size_hint_y=None,
            height="45dp",
            spacing=10,
        )
        popup = Popup(
            title=i18n.get("confirmation_title"),
            content=content,
            size_hint=(0.85, 0.35),
            auto_dismiss=False,
        )

        yes_button = Button(text=i18n.get("confirm"))
        no_button = Button(text=i18n.get("cancel"))

        yes_button.bind(
            on_release=lambda *_: (
                popup.dismiss(),
                self.delete_contact(),
            )
        )
        no_button.bind(on_release=popup.dismiss)

        buttons.add_widget(yes_button)
        buttons.add_widget(no_button)
        content.add_widget(buttons)
        popup.open()

    def delete_contact(self):
        if self.contact is None:
            self.ids.error_label.text = i18n.get("contact_empty")
            return

        try:
            # Сначала удаляем историю чата
            delete_messages(self.contact.guid)

            # Затем удаляем контакт
            delete_contact(self.contact.guid)

        except OSError:
            self.ids.error_label.text = i18n.get("delete_contact_fail")
            return

        except ValueError as error:
            self.ids.error_label.text = str(error)
            return

        self.contact = None

        self.manager.transition.direction = "right"
        self.manager.current = "main"

    def cancel(self):
        self.manager.transition.direction = "right"
        self.manager.current = "main"
