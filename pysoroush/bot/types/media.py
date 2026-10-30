"""
Media-related types for the Soroush Plus Bot API.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ._base import BaseType


@dataclass
class PhotoSize(BaseType):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    file_size: Optional[int] = None


@dataclass
class Animation(BaseType):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    duration: int
    thumb: Optional[PhotoSize] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


@dataclass
class Audio(BaseType):
    file_id: str
    file_unique_id: str
    duration: int
    performer: Optional[str] = None
    title: Optional[str] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    thumb: Optional[PhotoSize] = None


@dataclass
class Document(BaseType):
    file_id: str
    file_unique_id: str
    thumb: Optional[PhotoSize] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


@dataclass
class Video(BaseType):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    duration: int
    thumb: Optional[PhotoSize] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


@dataclass
class VideoNote(BaseType):
    file_id: str
    file_unique_id: str
    length: int
    duration: int
    thumb: Optional[PhotoSize] = None
    file_size: Optional[int] = None


@dataclass
class Voice(BaseType):
    file_id: str
    file_unique_id: str
    duration: int
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


@dataclass
class Contact(BaseType):
    phone_number: str
    first_name: str
    last_name: Optional[str] = None
    user_id: Optional[int] = None
    vcard: Optional[str] = None


@dataclass
class Location(BaseType):
    latitude: float
    longitude: float


@dataclass
class MaskPosition(BaseType):
    point: str
    x_shift: float
    y_shift: float
    scale: float


@dataclass
class Sticker(BaseType):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    is_animated: bool
    is_video: bool
    thumb: Optional[PhotoSize] = None
    emoji: Optional[str] = None
    set_name: Optional[str] = None
    mask_position: Optional[MaskPosition] = None
    file_size: Optional[int] = None
