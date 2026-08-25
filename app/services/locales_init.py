"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from shutil import copyfile
from pathlib import Path
from kivy.utils import platform
from app.services.logger import logger
from app.services.paths import LOCALES_DIR

BASE_DIR = Path(__file__).resolve().parents[1]
BUNDLED_LOCALES_DIR = BASE_DIR / ("data/locales" if platform == "android" else "data\\locales")


def install_locales():
    logger.info("Locales install started")
    if not BUNDLED_LOCALES_DIR.exists():
        logger.warning(f"Not found locales in {BUNDLED_LOCALES_DIR}")
        return

    LOCALES_DIR.mkdir(parents=True, exist_ok=True)

    for source_file in BUNDLED_LOCALES_DIR.glob("*.json"):
        target_file = LOCALES_DIR / source_file.name

        # Не перезаписываем переводы, изменённые пользователем
        if target_file.exists():
            continue

        try:
            logger.info(f"Coping locale {source_file.name}")
            copyfile(source_file, target_file)

        except OSError:
            logger.exception(f"Cannot copy locale {source_file} to {target_file}")
