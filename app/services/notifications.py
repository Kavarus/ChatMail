"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from kivy.utils import platform
from app.services.logger import logger

NOTIFICATION_ID = 1001
CHANNEL_ID = "chatmail_messages"


def show_new_message_marker(count=1):
    if platform != "android":
        return

    try:
        from jnius import autoclass

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Context = autoclass("android.content.Context")
        NotificationManager = autoclass("android.app.NotificationManager")
        NotificationChannel = autoclass("android.app.NotificationChannel")
        NotificationBuilder = autoclass("android.app.Notification$Builder")
        BuildVersion = autoclass("android.os.Build$VERSION")

        activity = PythonActivity.mActivity
        manager = activity.getSystemService(
            Context.NOTIFICATION_SERVICE
        )

        if BuildVersion.SDK_INT >= 26:
            channel = NotificationChannel(
                CHANNEL_ID,
                "Новые сообщения",
                NotificationManager.IMPORTANCE_DEFAULT,
            )
            manager.createNotificationChannel(channel)

        builder = NotificationBuilder(activity, CHANNEL_ID)

        app_info = activity.getApplicationInfo()

        notification = (
            builder
            .setSmallIcon(app_info.icon)
            .setContentTitle("ChatMail")
            .setContentText(f"Новых сообщений: {count}")
            .setNumber(int(count))
            .setAutoCancel(True)
            .build()
        )

        manager.notify(NOTIFICATION_ID, notification)
        logger.info("New-message marker shown: %d", count)

    except Exception:
        logger.exception("Cannot show new-message marker")


def clear_new_message_marker():
    if platform != "android":
        return

    try:
        from jnius import autoclass

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Context = autoclass("android.content.Context")

        activity = PythonActivity.mActivity
        manager = activity.getSystemService(
            Context.NOTIFICATION_SERVICE
        )

        manager.cancel(NOTIFICATION_ID)
        logger.info("New-message marker cleared")

    except Exception:
        logger.exception("Cannot clear new-message marker")
