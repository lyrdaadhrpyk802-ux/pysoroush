"""Tests for message filters."""

from pysoroush.bot.filters import Text, Photo, Private, Group
from pysoroush.bot.types import Message, Chat, PhotoSize, Update


def create_message(text: str = None, is_photo: bool = False, chat_type: str = "private") -> Message:
    return Message(
        message_id=1,
        date=123,
        chat=Chat(id=1, type=chat_type),
        text=text,
        photo=[PhotoSize(file_id="1", file_unique_id="1", width=10, height=10)] if is_photo else None
    )


def test_text_filter() -> None:
    f = Text("hello")
    assert f(create_message(text="hello")) is True
    assert f(create_message(text="world")) is False
    assert f(create_message(text=None)) is False


def test_photo_filter() -> None:
    f = Photo()
    assert f(create_message(is_photo=True)) is True
    assert f(create_message(is_photo=False)) is False


def test_chat_type_filter() -> None:
    priv = Private()
    grp = Group()
    
    assert priv(create_message(chat_type="private")) is True
    assert priv(create_message(chat_type="group")) is False
    assert grp(create_message(chat_type="group")) is True
    assert grp(create_message(chat_type="private")) is False


def test_combined_filters() -> None:
    # AND filter
    f_and = Text("hello") & Private()
    assert f_and(create_message(text="hello", chat_type="private")) is True
    assert f_and(create_message(text="hello", chat_type="group")) is False

    # OR filter
    f_or = Text("hello") | Photo()
    assert f_or(create_message(text="hello")) is True
    assert f_or(create_message(is_photo=True)) is True
    assert f_or(create_message(text="world")) is False

    # NOT filter
    f_not = ~Private()
    assert f_not(create_message(chat_type="group")) is True
    assert f_not(create_message(chat_type="private")) is False


def test_bot_with_filters() -> None:
    from pysoroush.bot.bot import Bot
    bot = Bot("123456:ABC")
    called = False

    @bot.on_message(Photo() & Private())
    def photo_handler(msg: Message):
        nonlocal called
        called = True

    # Should trigger
    update1 = Update(
        update_id=1, 
        message=create_message(is_photo=True, chat_type="private")
    )
    bot._process_update(update1)
    assert called is True

    # Should NOT trigger (wrong chat type)
    called = False
    update2 = Update(
        update_id=2, 
        message=create_message(is_photo=True, chat_type="group")
    )
    bot._process_update(update2)
    assert called is False
