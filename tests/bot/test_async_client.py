"""Tests for the asynchronous AsyncClient."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from pysoroush.bot.async_client import AsyncClient
from pysoroush.bot.types import User, Message


@pytest.mark.asyncio
async def test_async_get_me() -> None:
    client = AsyncClient("123456:ABC-DEF")
    
    # Mock the request method
    client.request = AsyncMock(return_value={
        "id": 123,
        "is_bot": True,
        "first_name": "TestBot",
        "username": "test_bot"
    })

    user = await client.get_me()
    
    assert isinstance(user, User)
    assert user.id == 123
    assert user.username == "test_bot"
    client.request.assert_called_once_with("getMe")


@pytest.mark.asyncio
async def test_async_send_message() -> None:
    client = AsyncClient("123456:ABC-DEF")
    
    client.request = AsyncMock(return_value={
        "message_id": 1,
        "date": 1234567890,
        "chat": {"id": 123, "type": "private"},
        "text": "Hello"
    })

    msg = await client.send_message(chat_id=123, text="Hello")
    
    assert isinstance(msg, Message)
    assert msg.text == "Hello"
    assert msg.message_id == 1
    
    # Check if request was called correctly
    client.request.assert_called_once()
    args, kwargs = client.request.call_args
    assert args[0] == "sendMessage"
    assert kwargs["data"]["chat_id"] == 123
    assert kwargs["data"]["text"] == "Hello"
