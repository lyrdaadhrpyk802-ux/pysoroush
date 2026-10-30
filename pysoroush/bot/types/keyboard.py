"""
Keyboard-related types for the Soroush Plus Bot API.
Includes Fluent Builder methods for easier creation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union

from ._base import BaseType


@dataclass
class InlineKeyboardButton(BaseType):
    text: str
    url: Optional[str] = None
    callback_data: Optional[str] = None


@dataclass
class InlineKeyboardMarkup(BaseType):
    inline_keyboard: List[List[InlineKeyboardButton]] = field(default_factory=list)

    def row(self, *buttons: Union[str, InlineKeyboardButton]) -> "InlineKeyboardMarkup":
        """
        Add a new row of buttons. Accepts strings or InlineKeyboardButton objects.
        Example: keyboard.row("Yes", "No")
        """
        row_list = []
        for b in buttons:
            if isinstance(b, str):
                row_list.append(InlineKeyboardButton(text=b))
            elif isinstance(b, InlineKeyboardButton):
                row_list.append(b)
        self.inline_keyboard.append(row_list)
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "inline_keyboard": [
                [b.to_dict() for b in row] for row in self.inline_keyboard
            ]
        }


@dataclass
class KeyboardButton(BaseType):
    text: str
    request_contact: Optional[bool] = None
    request_location: Optional[bool] = None


@dataclass
class ReplyKeyboardMarkup(BaseType):
    keyboard: List[List[KeyboardButton]] = field(default_factory=list)
    resize_keyboard: Optional[bool] = None
    one_time_keyboard: Optional[bool] = None
    input_field_placeholder: Optional[str] = None

    def row(self, *buttons: Union[str, KeyboardButton]) -> "ReplyKeyboardMarkup":
        """
        Add a new row of buttons. Accepts strings or KeyboardButton objects.
        Example: keyboard.row("Cancel").row("Confirm")
        """
        row_list = []
        for b in buttons:
            if isinstance(b, str):
                row_list.append(KeyboardButton(text=b))
            elif isinstance(b, KeyboardButton):
                row_list.append(b)
        self.keyboard.append(row_list)
        return self

    def resize(self, resize: bool = True) -> "ReplyKeyboardMarkup":
        self.resize_keyboard = resize
        return self

    def one_time(self, one_time: bool = True) -> "ReplyKeyboardMarkup":
        self.one_time_keyboard = one_time
        return self

    def to_dict(self) -> Dict[str, Any]:
        res = {
            "keyboard": [
                [b.to_dict() for b in row] for row in self.keyboard
            ]
        }
        if self.resize_keyboard is not None:
            res["resize_keyboard"] = self.resize_keyboard
        if self.one_time_keyboard is not None:
            res["one_time_keyboard"] = self.one_time_keyboard
        if self.input_field_placeholder is not None:
            res["input_field_placeholder"] = self.input_field_placeholder
        return res


@dataclass
class ReplyKeyboardRemove(BaseType):
    remove_keyboard: bool = True
    selective: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        res = {"remove_keyboard": self.remove_keyboard}
        if self.selective is not None:
            res["selective"] = self.selective
        return res


@dataclass
class ForceReply(BaseType):
    force_reply: bool = True
    input_field_placeholder: Optional[str] = None
    selective: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        res = {"force_reply": self.force_reply}
        if self.input_field_placeholder is not None:
            res["input_field_placeholder"] = self.input_field_placeholder
        if self.selective is not None:
            res["selective"] = self.selective
        return res
