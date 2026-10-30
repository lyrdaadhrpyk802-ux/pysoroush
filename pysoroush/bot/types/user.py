"""
User-related types for the Soroush Plus Bot API.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List

from ._base import BaseType
from .media import PhotoSize


@dataclass
class User(BaseType):
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    can_join_groups: Optional[bool] = None
    can_read_all_group_messages: Optional[bool] = None
    supports_inline_queries: Optional[bool] = None


@dataclass
class UserProfilePhotos(BaseType):
    total_count: int
    photos: List[List[PhotoSize]]
