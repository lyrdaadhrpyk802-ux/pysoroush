"""Tests for the type definitions in pysoroush.bot.types."""

from pysoroush.bot.types import (
    User,
    Chat,
    Message,
    MessageEntity,
)


def test_user_from_dict() -> None:
    data = {
        "id": 123,
        "is_bot": False,
        "first_name": "Ali",
        "last_name": "VEX",
        "username": "lyrdaadhrpyk802",
        "language_code": "fa",
    }
    user = User.from_dict(data)
    assert user.id == 123
    assert user.first_name == "Ali"
    assert user.last_name == "VEX"
    assert user.username == "lyrdaadhrpyk802"
    assert user.language_code == "fa"


def test_chat_from_dict() -> None:
    data = {
        "id": 456,
        "type": "private",
        "first_name": "Ali",
        "last_name": "VEX",
        "username": "lyrdaadhrpyk802",
    }
    chat = Chat.from_dict(data)
    assert chat.id == 456
    assert chat.type == "private"
    assert chat.first_name == "Ali"


def test_message_from_dict() -> None:
    data = {
        "message_id": 789,
        "date": 1600000000,
        "chat": {
            "id": 456,
            "type": "private",
        },
        "from": {
            "id": 123,
            "is_bot": False,
            "first_name": "Ali",
        },
        "text": "Hello",
        "entities": [
            {"type": "bold", "offset": 0, "length": 5}
        ]
    }
    msg = Message.from_dict(data)
    assert msg.message_id == 789
    assert msg.date == 1600000000
    assert isinstance(msg.chat, Chat)
    assert msg.chat.id == 456
    assert isinstance(msg.from_user, User)
    assert msg.from_user.first_name == "Ali"
    assert msg.text == "Hello"
    assert isinstance(msg.entities, list)
    assert len(msg.entities) == 1
    assert isinstance(msg.entities[0], MessageEntity)
    assert msg.entities[0].type == "bold"


def test_message_to_dict() -> None:
    msg = Message(
        message_id=789,
        date=1600000000,
        chat=Chat(id=456, type="private"),
        from_user=User(id=123, is_bot=False, first_name="Ali"),
        text="Hello",
    )
    data = msg.to_dict()
    assert data["message_id"] == 789
    assert data["chat"]["id"] == 456
    assert data["from"]["id"] == 123
    assert "entities" not in data
