"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import NumericProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window


class SafeAreaBoxLayout(BoxLayout):
    safe_top = NumericProperty(dp(24))
    safe_bottom = NumericProperty(dp(16))
    safe_left = NumericProperty(0)
    safe_right = NumericProperty(0)

    use_system_insets = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(size=self._on_window_changed, on_config_change=self._on_window_config_change)
        Clock.schedule_once(self.update_insets, 0)

    def _on_window_changed(self, *_):
        self.update_insets()

    def _on_window_config_change(self, *_):
        self.update_insets()

    def update_insets(self, *_):
        if not self.use_system_insets:
            return

        top = getattr(Window, "inset_top", 0)
        bottom = getattr(Window, "inset_bottom", 0)
        left = getattr(Window, "inset_left", 0)
        right = getattr(Window, "inset_right", 0)

        try:
            top = float(top or 0)
            bottom = float(bottom or 0)
            left = float(left or 0)
            right = float(right or 0)
        except (TypeError, ValueError):
            top = bottom = left = right = 0

        # Сохраняем гарантированный отступ в 36dp сверху и 36dp снизу.
        self.safe_top = max(dp(36), top)
        self.safe_bottom = max(dp(36), bottom)
        self.safe_left = max(dp(5), left)
        self.safe_right = max(dp(5), right)
        self.padding = (
            self.safe_left,
            self.safe_bottom,
            self.safe_right,
            self.safe_top,
        )
