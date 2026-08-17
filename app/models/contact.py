"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from dataclasses import dataclass, asdict


@dataclass
class Contact:
    name: str
    email: str
    has_new_messages: bool = False

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            email=data["email"],
            has_new_messages=data.get("has_new_messages", False),
        )
