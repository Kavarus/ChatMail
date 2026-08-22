"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

import logging
import sys
import threading
from app.services.paths import DATA_DIR

LOG_FILE = DATA_DIR / "chatmail.log"


def setup_logging():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )

    app_logger = logging.getLogger("chatmail")

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        app_logger.critical(
            "Exception",
            exc_info=(exc_type, exc_value, exc_traceback),
        )

    sys.excepthook = handle_exception

    if hasattr(threading, "excepthook"):
        def handle_thread_exception(args):
            app_logger.critical(
                "Exception in thread %s",
                args.thread.name if args.thread else "unknown",
                exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
            )

        threading.excepthook = handle_thread_exception

    app_logger.info("===== ===== ===== =====")
    app_logger.info("Logger started")
    app_logger.info("File: %s", LOG_FILE)

    return app_logger


logger = setup_logging()
