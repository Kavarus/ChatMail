"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

import json
from pathlib import Path
from kivy.properties import StringProperty
from kivy.event import EventDispatcher
from app.services.logger import logger
from app.services.paths import LOCALES_DIR

DEFAULT_LANGUAGE = "ru"
DEFAULT_TRANSLATION = {
    "language_name": "Русский",

    "welcome_title": "ПочтоЧат",
    "welcome_text": (
        "Это приложение позволяет общаться с выбранными контактами "
        "в формате чата через почтовый сервис.\n\n"
        "Для работы приложения следует использовать пароль для приложений. "
        "Сообщения будут получены только от заранее добавленных контактов."
    ),
    "terms_title": "Условия использования",
    "terms_text": (
        "Используя приложение, вы подтверждаете, что:\n"
        "• принимаете приложение и его функции «как есть»;\n"
        "• самостоятельно настраиваете подключение к почтовому сервису;\n"
        "• разрешаете приложению получать и отправлять сообщения;\n"
        "• несете полную ответственность за используемые учетные данные, настройки и действия в приложении;\n"
        "• понимаете, что приложение может работать с ошибками и не гарантирует своевременной отправки и получения сообщений;\n"
        "• не используете приложение для незаконной рассылки и не нарушаете права третьих лиц.\n\n"
        "Приложение предоставляется без каких-либо гарантий. "
        "Разработчик не отвечает за любые прямые или косвенные последствия его использования, "
        "включая потерю данных, сообщений, доступа к почтовому аккаунту, финансовые убытки и иной ущерб. "
        "Все риски и ответственность за использование приложения полностью несет пользователь.\n\n"
        "Продолжая работу, вы подтверждаете, что ознакомились с этими условиями, понимаете их и принимаете их. "
        "Претензии к последствиям использования приложения не принимаются."
    ),
    "select_language": "Язык",
    "accept": "Принять",
    "main_title": "Контакты",
    "settings": "Настройки",
    "add_contact": "Добавить контакт",
    "back": "Назад",
    "checking": "Проверка...",
    "save": "Сохранить",
    "cancel": "Отмена",
    "send": "Отправить",
    "sending": "Отправка...",
    "send_error": "Ошибка отправки: {error}",
    "message_sent": "Сообщение отправлено",
    "message_hint": "Введите сообщение",
    "mail_provider": "Почтовый сервис",
    "email": "Почта",
    "password": "Пароль",
    "password_hint": "Для подключения используется пароль приложения, который нужно заранее создать в почтовом сервисе.",
    "contact_name": "Имя",
    "contact_address": "Адрес",
    "contact_empty": "Контакт не выбран",
    "contact_fields_required": "Заполните имя и адрес",
    "edit_contact": "Редактирование контакта",
    "delete_contact": "Удалить контакт",
    "delete_confirmation": "Удалить контакт и всю историю чата?",
    "confirmation_title": "Подтверждение удаления",
    "confirm": "Подтвердить",
    "close": "Закрыть",
    "delete_contact_fail": "Не удалось завершить удаление чата",
    "provider_required": "Выберите почтовый сервис",
    "email_required": "Введите адрес почты",
    "password_required": "Введите пароль",
    "settings_saved": "Настройки успешно сохранены",
    "connection_error": "Ошибка подключения. Проверьте настройки",
    "application_settings": "Настройки приложения",
    "connection_settings": "Настройки подключения",
    "active_interval": "Интервал проверки почты в активном приложении, секунд",
    "background_interval": "Интервал проверки почты в свернутом приложении, секунд",
    "interval_invalid": "Интервал должен быть положительным числом",
    "bug_report": "Сообщить об ошибке",
    "bug_report_hint": "Опишите проблему",
    "bug_report_sent": "Сообщение отправлено",
    "bug_report_error": "Не удалось отправить сообщение",
}


class I18n(EventDispatcher):
    language = StringProperty(DEFAULT_LANGUAGE)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_language_changed")
        self.translations = {}
        self.language_names = {}
        self.available_languages = []

        self.reload()

    def reload(self):
        """
        Перезагружает JSON-файлы локализации:
        - если JSON-файлов нет, используется встроенный русский;
        - если есть хотя бы один JSON-файл, встроенный русский не используется.
        """
        loaded_translations = {}
        loaded_language_names = {}

        LOCALES_DIR.mkdir(parents=True, exist_ok=True)

        for file_path in sorted(LOCALES_DIR.glob("*.json")):
            language = file_path.stem.lower().strip()

            if not language:
                continue

            try:
                with file_path.open("r", encoding="utf-8") as file:
                    data = json.load(file)

            except (OSError, json.JSONDecodeError) as error:
                logger.warning("Localization file cannot be loaded: %s (%s)", file_path, error)
                continue

            if not isinstance(data, dict):
                logger.warning("Localization file must contain a JSON object: %s", file_path)
                continue

            language_name = data.pop("language_name", language)

            if not isinstance(language_name, str):
                language_name = language

            loaded_translations[language] = data
            loaded_language_names[language] = language_name

        if loaded_translations:
            self.translations = loaded_translations
            self.language_names = loaded_language_names
        else:
            self.translations = {
                DEFAULT_LANGUAGE: DEFAULT_TRANSLATION.copy()
            }
            self.language_names = {
                DEFAULT_LANGUAGE: DEFAULT_TRANSLATION["language_name"]
            }

        self.available_languages = sorted(self.translations.keys())

        if self.language not in self.translations:
            self.language = self.available_languages[0]

        logger.info("Available languages: %s", ", ".join(self.available_languages))

    def get_available_languages(self):
        return list(self.available_languages)

    def get_language_items(self):
        return [(self.language_names[language], language) for language in self.available_languages]

    def set_language(self, language):
        language = str(language).lower().strip()

        if language not in self.translations:
            logger.warning("Unknown language requested: %s", language)
            return False

        if self.language == language:
            return True

        self.language = language
        self.dispatch("on_language_changed")
        return True

    def get(self, key):
        language_data = self.translations.get(self.language, {})

        if key in language_data:
            return language_data[key]

        logger.warning("Missing translation key '%s' for language '%s'", key, self.language)
        if key in DEFAULT_TRANSLATION:
            return DEFAULT_TRANSLATION[key]

        logger.warning("Missing translation key '%s' for default language", key)
        return key

    def get_language_name(self, language):
        return self.language_names.get(language, language)

    def on_language_changed(self):
        pass


i18n = I18n()
