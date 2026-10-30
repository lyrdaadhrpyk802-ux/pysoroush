"""
Built-in filters for message handlers.
"""

from __future__ import annotations

import re
from typing import Optional

from ..types import Message


class Filter:
    def __call__(self, message: Message) -> bool:
        return True

    def __and__(self, other: "Filter") -> "AndFilter":
        return AndFilter(self, other)

    def __or__(self, other: "Filter") -> "OrFilter":
        return OrFilter(self, other)

    def __invert__(self) -> "InvertFilter":
        return InvertFilter(self)


class AndFilter(Filter):
    def __init__(self, f1: Filter, f2: Filter) -> None:
        self.f1 = f1
        self.f2 = f2

    def __call__(self, message: Message) -> bool:
        return self.f1(message) and self.f2(message)


class OrFilter(Filter):
    def __init__(self, f1: Filter, f2: Filter) -> None:
        self.f1 = f1
        self.f2 = f2

    def __call__(self, message: Message) -> bool:
        return self.f1(message) or self.f2(message)


class InvertFilter(Filter):
    def __init__(self, f: Filter) -> None:
        self.f = f

    def __call__(self, message: Message) -> bool:
        return not self.f(message)


class Text(Filter):
    def __init__(self, text: str) -> None:
        self.text = text

    def __call__(self, message: Message) -> bool:
        return message.text == self.text


class Regex(Filter):
    def __init__(self, pattern: str) -> None:
        self.pattern = re.compile(pattern)

    def __call__(self, message: Message) -> bool:
        if not message.text:
            return False
        return bool(self.pattern.search(message.text))


class Photo(Filter):
    def __call__(self, message: Message) -> bool:
        return message.photo is not None


class Document(Filter):
    def __call__(self, message: Message) -> bool:
        return message.document is not None


class Video(Filter):
    def __call__(self, message: Message) -> bool:
        return message.video is not None


class Voice(Filter):
    def __call__(self, message: Message) -> bool:
        return message.voice is not None


class Contact(Filter):
    def __call__(self, message: Message) -> bool:
        return message.contact is not None


class Location(Filter):
    def __call__(self, message: Message) -> bool:
        return message.location is not None


class Private(Filter):
    def __call__(self, message: Message) -> bool:
        return message.chat.type == "private"


class Group(Filter):
    def __call__(self, message: Message) -> bool:
        return message.chat.type in ("group", "supergroup")


class Channel(Filter):
    def __call__(self, message: Message) -> bool:
        return message.chat.type == "channel"


class StateFilter(Filter):
    """
    Filter that checks if the message has a specific FSM state.
    """
    def __init__(self, state: str) -> None:
        self.state = state

    def __call__(self, message: Message) -> bool:
        return message.state == self.state
