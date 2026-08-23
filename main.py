"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from kivy.utils import platform
if platform == "win":
    from kivy.config import Config
    Config.set("graphics", "width", "450")
    Config.set("graphics", "height", "800")
    Config.set("graphics", "resizable", "1")

from app.services.locales_init import install_locales
try:
    install_locales()
except Exception:
    import traceback
    traceback.print_exc()

from app.application import ChatApp
if __name__ == "__main__":
    ChatApp().run()
