"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from app.services.locales_init import install_locales
install_locales()

from app.app import ChatApp
if __name__ == "__main__":
    ChatApp().run()
