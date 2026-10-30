"""
InputMedia types for sending albums and editing media.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List

from ._base import BaseType
from .message import MessageEntity
from .input_file import InputFile


@dataclass
class InputMediaPhoto(BaseType):
    type: str = "photo"
    media: str = ""
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    caption_entities: Optional[List[MessageEntity]] = None


@dataclass
class InputMediaVideo(BaseType):
    type: str = "video"
    media: str = ""
    thumb: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    caption_entities: Optional[List[MessageEntity]] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None
    supports_streaming: Optional[bool] = None


@dataclass
class InputMediaAudio(BaseType):
    type: str = "audio"
    media: str = ""
    thumb: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    caption_entities: Optional[List[MessageEntity]] = None
    duration: Optional[int] = None
    performer: Optional[str] = None
    title: Optional[str] = None


@dataclass
class InputMediaDocument(BaseType):
    type: str = "document"
    media: str = ""
    thumb: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    caption_entities: Optional[List[MessageEntity]] = None
    disable_content_type_detection: Optional[bool] = None
