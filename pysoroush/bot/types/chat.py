"""
Chat-related types for the Soroush Plus Bot API.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from ._base import BaseType

if TYPE_CHECKING:
    from .message import Message


@dataclass
class ChatPhoto(BaseType):
    small_file_id: str
    small_file_unique_id: str
    big_file_id: str
    big_file_unique_id: str


@dataclass
class Chat(BaseType):
    id: int
    type: str
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo: Optional[ChatPhoto] = None
    bio: Optional[str] = None
    description: Optional[str] = None
    invite_link: Optional[str] = None
    pinned_message: Optional[Message] = None
    slow_mode_delay: Optional[int] = None
    message_auto_delete_time: Optional[int] = None
    has_protected_content: Optional[bool] = None
    sticker_set_name: Optional[str] = None
    can_set_sticker_set: Optional[bool] = None
    linked_chat_id: Optional[int] = None
    all_members_are_administrators: Optional[bool] = None
