"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

import time

from app.services.logger import logger
from app.services.storage import (load_settings, has_mail_settings)
from app.services.mail_poller import MailPoller

BACKGROUND_MAIL_INTERVAL = 300


def run():
    logger.info("Foreground mail service started")

    settings = load_settings()

    if not has_mail_settings(settings):
        logger.info("Foreground service stopped: mail settings are empty")
        return

    poller = MailPoller(settings)

    while True:
        started_at = time.monotonic()

        try:
            messages = poller.check()
            logger.info("Background mail check completed. New messages: %d", len(messages))

        except Exception:
            logger.exception("Background mail check failed")

        elapsed = time.monotonic() - started_at
        delay = max(1, BACKGROUND_MAIL_INTERVAL - elapsed)
        time.sleep(delay)


if __name__ == "__main__":
    run()
