"""
Copyright (C) 2026 Alexandr Kavaru
SPDX-License-Identifier: GPL-3.0-or-later
This file is part of ChatMail application.
"""

from dataclasses import dataclass, asdict
from uuid import uuid4


@dataclass
class Contact:
    name: str
    email: str
    guid: str
    has_new_messages: bool = False

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name", ""),
            email=data.get("email", ""),
            guid=data.get("guid") or str(uuid4()),
            has_new_messages=data.get("has_new_messages", False),
        )
