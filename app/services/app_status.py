"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from datetime import datetime
from kivy.clock import mainthread
from kivy.event import EventDispatcher
from kivy.properties import StringProperty
from app.services.logger import logger


class AppStatus(EventDispatcher):
    text = StringProperty("")
    level = StringProperty("info")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_status_changed")

    def set(self, message, level="info", log=True):
        message = str(message)
        now = datetime.now().astimezone()
        timestamp = now.strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}"

        if log:
            if level == "error":
                logger.error(message)
            elif level == "warning":
                logger.warning(message)
            else:
                logger.info(message)
        self._set_on_main_thread(full_message, level)

    @mainthread
    def _set_on_main_thread(self, message, level):
        self.text = message
        self.level = level
        self.dispatch("on_status_changed")

    def clear(self):
        self.set("", level="info", log=False)

    def on_status_changed(self):
        pass


app_status = AppStatus()
