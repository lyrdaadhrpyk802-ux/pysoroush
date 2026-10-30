"""
BotCommand and BotCommandScope types.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Union

from ._base import BaseType


@dataclass
class BotCommand(BaseType):
    command: str
    description: str


@dataclass
class BotCommandScopeDefault(BaseType):
    type: str = "default"


@dataclass
class BotCommandScopeAllPrivateChats(BaseType):
    type: str = "all_private_chats"


@dataclass
class BotCommandScopeChat(BaseType):
    type: str = "chat"
    chat_id: Union[int, str] = ""
