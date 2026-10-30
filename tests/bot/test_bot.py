"""Tests for the high-level Bot class (dispatcher and polling)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from pysoroush.bot.bot import Bot
from pysoroush.bot.async_bot import AsyncBot
from pysoroush.bot.types import Update, Message, Chat, User


def test_bot_command_handler() -> None:
    bot = Bot("123456:ABC")
    called = False

    @bot.command("start")
    def start_handler(msg: Message):
        nonlocal called
        called = True

    update = Update(
        update_id=1,
        message=Message(
            message_id=1,
            date=123,
            chat=Chat(id=1, type="private"),
            text="/start"
        )
    )

    bot._process_update(update)
    assert called is True


def test_bot_command_handler_with_botname() -> None:
    bot = Bot("123456:ABC")
    called = False

    @bot.command("start")
    def start_handler(msg: Message):
        nonlocal called
        called = True

    update = Update(
        update_id=1,
        message=Message(
            message_id=1,
            date=123,
            chat=Chat(id=1, type="private"),
            text="/start@my_awesome_bot"
        )
    )

    bot._process_update(update)
    assert called is True


def test_bot_on_message_handler() -> None:
    bot = Bot("123456:ABC")
    called = False

    @bot.on_message()
    def msg_handler(msg: Message):
        nonlocal called
        called = True

    update = Update(
        update_id=1,
        message=Message(
            message_id=1,
            date=123,
            chat=Chat(id=1, type="private"),
            text="hello"
        )
    )

    bot._process_update(update)
    assert called is True


@pytest.mark.asyncio
async def test_async_bot_command_handler() -> None:
    bot = AsyncBot("123456:ABC")
    called = False

    @bot.command("start")
    async def start_handler(msg: Message):
        nonlocal called
        called = True

    update = Update(
        update_id=1,
        message=Message(
            message_id=1,
            date=123,
            chat=Chat(id=1, type="private"),
            text="/start"
        )
    )

    await bot._process_update(update)
    assert called is True
