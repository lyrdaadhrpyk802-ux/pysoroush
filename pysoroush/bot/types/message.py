"""
Message-related types for the Soroush Plus Bot API.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Dict, Any, TYPE_CHECKING

from ._base import BaseType
from .user import User
from .media import (
    PhotoSize, Animation, Audio, Document, Video, VideoNote, Voice,
    Contact, Location, Sticker,
)

if TYPE_CHECKING:
    from .chat import Chat


@dataclass
class MessageEntity(BaseType):
    type: str
    offset: int
    length: int
    url: Optional[str] = None
    user: Optional[User] = None
    language: Optional[str] = None


@dataclass
class MessageId(BaseType):
    message_id: int


@dataclass
class Message(BaseType):
    message_id: int
    date: int
    chat: Chat
    from_user: Optional[User] = None
    forward_from: Optional[User] = None
    forward_from_chat: Optional[Chat] = None
    forward_from_message_id: Optional[int] = None
    forward_signature: Optional[str] = None
    forward_sender_name: Optional[str] = None
    forward_date: Optional[int] = None
    reply_to_message: Optional[Message] = None
    via_bot: Optional[User] = None
    edit_date: Optional[int] = None
    has_protected_content: Optional[bool] = None
    media_group_id: Optional[str] = None
    text: Optional[str] = None
    entities: Optional[List[MessageEntity]] = None
    animation: Optional[Animation] = None
    audio: Optional[Audio] = None
    document: Optional[Document] = None
    photo: Optional[List[PhotoSize]] = None
    sticker: Optional[Sticker] = None
    video: Optional[Video] = None
    video_note: Optional[VideoNote] = None
    voice: Optional[Voice] = None
    caption: Optional[str] = None
    caption_entities: Optional[List[MessageEntity]] = None
    contact: Optional[Contact] = None
    location: Optional[Location] = None
    new_chat_title: Optional[str] = None
    new_chat_photo: Optional[List[PhotoSize]] = None
    pinned_message: Optional[Message] = None
    reply_markup: Optional[dict] = None
    
    # Internal field to hold FSM state (not sent by the API)
    state: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        if not data:
            return None
        data = dict(data)
        if "from" in data:
            data["from_user"] = data.pop("from")
        return super().from_dict(data)

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        if "from_user" in data:
            data["from"] = data.pop("from_user")
        if "state" in data:
            data.pop("state") # Remove before sending to API
        return data
