"""
Update and Webhook-related types for the Soroush Plus Bot API.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Dict, Any, TYPE_CHECKING

from ._base import BaseType
from .user import User
from .message import Message

if TYPE_CHECKING:
    pass


@dataclass
class ResponseParameters(BaseType):
    retry_after: Optional[int] = None


@dataclass
class CallbackQuery(BaseType):
    id: str
    from_user: User
    message: Optional[Message] = None
    data: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CallbackQuery":
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
        return data


@dataclass
class Update(BaseType):
    update_id: int
    message: Optional[Message] = None
    edited_message: Optional[Message] = None
    callback_query: Optional[CallbackQuery] = None


@dataclass
class WebhookInfo(BaseType):
    url: str
    has_custom_certificate: bool
    pending_update_count: int
    ip_address: Optional[str] = None
    last_error_date: Optional[int] = None
    last_error_message: Optional[str] = None
    max_connections: Optional[int] = None
    allowed_updates: Optional[List[str]] = None
