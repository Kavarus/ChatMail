"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

import time

from app.services.logger import logger
from app.services.storage import (load_settings, has_mail_settings, get_application_settings)
from app.services.mail_poller import MailPoller
from app.services.contacts import count_new_messages
from app.services.notifications import show_new_message_marker


def run():
    logger.info("Foreground mail service started")

    settings = load_settings()

    if not has_mail_settings(settings):
        logger.info("Foreground service stopped: mail settings are empty")
        return
    application_settings = get_application_settings(settings)
    background_interval = int(application_settings["background_mail_interval"])
    poller = MailPoller(settings)

    while True:
        started_at = time.monotonic()

        try:
            messages = poller.check()
            if messages:
                unread_count = count_new_messages()
                show_new_message_marker(unread_count)
            logger.info("Background mail check completed. New messages: %d", len(messages))

        except Exception as error:
            logger.exception(f"Background mail check failed: {error}")

        elapsed = time.monotonic() - started_at
        delay = max(
            1,
            background_interval - int(elapsed),
        )
        logger.info("Check delay: %d", delay)
        time.sleep(delay)


if __name__ == "__main__":
    run()
