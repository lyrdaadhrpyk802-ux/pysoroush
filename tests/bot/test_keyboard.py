"""Tests for keyboard types and Fluent Builder."""

from pysoroush.bot.types.keyboard import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)


def test_inline_keyboard_fluent_builder() -> None:
    # Test the chainable methods
    kb = InlineKeyboardMarkup()
    kb.row("Button 1", "Button 2").row(
        InlineKeyboardButton(text="Button 3", callback_data="data3")
    )

    data = kb.to_dict()
    assert "inline_keyboard" in data
    assert len(data["inline_keyboard"]) == 2
    
    row1 = data["inline_keyboard"][0]
    assert len(row1) == 2
    assert row1[0]["text"] == "Button 1"
    assert row1[1]["text"] == "Button 2"
    
    row2 = data["inline_keyboard"][1]
    assert len(row2) == 1
    assert row2[0]["text"] == "Button 3"
    assert row2[0]["callback_data"] == "data3"


def test_reply_keyboard_fluent_builder() -> None:
    kb = ReplyKeyboardMarkup()
    kb.row("Yes", "No").row(
        KeyboardButton(text="Share Contact", request_contact=True)
    ).resize(True).one_time(True)

    data = kb.to_dict()
    assert len(data["keyboard"]) == 2
    assert data["resize_keyboard"] is True
    assert data["one_time_keyboard"] is True
    
    row2 = data["keyboard"][1]
    assert row2[0]["text"] == "Share Contact"
    assert row2[0]["request_contact"] is True


def test_reply_keyboard_remove() -> None:
    rm = ReplyKeyboardRemove()
    data = rm.to_dict()
    assert data == {"remove_keyboard": True}


def test_inline_keyboard_from_dict() -> None:
    # Test deserialization just in case
    data = {
        "inline_keyboard": [
            [{"text": "Click me", "url": "https://example.com"}]
        ]
    }
    kb = InlineKeyboardMarkup.from_dict(data)
    assert isinstance(kb, InlineKeyboardMarkup)
    assert len(kb.inline_keyboard) == 1
    assert isinstance(kb.inline_keyboard[0][0], InlineKeyboardButton)
    assert kb.inline_keyboard[0][0].text == "Click me"
    assert kb.inline_keyboard[0][0].url == "https://example.com"
