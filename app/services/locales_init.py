"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

import json
from shutil import copyfile
from pathlib import Path
from kivy.utils import platform
from app.services.logger import logger
from app.services.paths import LOCALES_DIR

BASE_DIR = Path(__file__).resolve().parents[1]
BUNDLED_LOCALES_DIR = BASE_DIR / ("data/locales" if platform == "android" else "data\\locales")


def get_locale_version(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        version = data.get("loc_version", "0.0")

        if not isinstance(version, str):
            raise ValueError(f"Invalid locale version in {path}: {version!r}")

        return version

    except (OSError, json.JSONDecodeError, ValueError):
        logger.exception("Cannot read locale version from %s", path)
        return "0.0"


def is_new_version(old_version, new_version):
    old1, old2 = old_version.strip().split('.', maxsplit=1)
    new1, new2 = new_version.strip().split('.', maxsplit=1)
    if not old1.isdigit() or not old2.isdigit():
        return True
    if int(new1) > int(old1):
        return True
    if new1 == old1 and int(new2) > int(old2):
        return True
    return False


def install_locales():
    logger.info("Locales install started")
    if not BUNDLED_LOCALES_DIR.exists():
        logger.warning(f"Not found locales in {BUNDLED_LOCALES_DIR}")
        return

    LOCALES_DIR.mkdir(parents=True, exist_ok=True)

    for source_file in BUNDLED_LOCALES_DIR.glob("*.json"):
        target_file = LOCALES_DIR / source_file.name

        try:
            if not target_file.exists():
                logger.info(f"Copying new locale {source_file.name}")
                copyfile(source_file, target_file)
                continue

            bundled_version = get_locale_version(source_file)
            installed_version = get_locale_version(target_file)

            if is_new_version(installed_version, bundled_version):
                logger.info(f"Updating locale {source_file.name} to version {bundled_version}")
                copyfile(source_file, target_file)

        except OSError:
            logger.exception(f"Cannot copy locale {source_file} to {target_file}")
