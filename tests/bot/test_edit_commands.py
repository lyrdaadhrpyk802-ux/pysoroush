"""Tests for editing messages, deleting, callback queries, and commands."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from pysoroush.bot.client import Client
from pysoroush.bot.async_client import AsyncClient
from pysoroush.bot.types import Message, BotCommand


@patch("requests.Session.post")
def test_edit_message_text(mock_post: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ok": True,
        "result": {
            "message_id": 1,
            "date": 123,
            "chat": {"id": 1, "type": "private"},
            "text": "Edited text"
        }
    }
    mock_post.return_value = mock_response

    client = Client("123456:ABC-DEF")
    msg = client.edit_message_text(text="Edited text", chat_id=1, message_id=1)
    
    assert isinstance(msg, Message)
    assert msg.text == "Edited text"


@patch("requests.Session.post")
def test_delete_message(mock_post: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ok": True, "result": True}
    mock_post.return_value = mock_response

    client = Client("123456:ABC-DEF")
    success = client.delete_message(chat_id=1, message_id=10)
    
    assert success is True
    args, kwargs = mock_post.call_args
    assert kwargs["data"]["chat_id"] == 1
    assert kwargs["data"]["message_id"] == 10


@patch("requests.Session.post")
def test_answer_callback_query(mock_post: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ok": True, "result": True}
    mock_post.return_value = mock_response

    client = Client("123456:ABC-DEF")
    success = client.answer_callback_query(callback_query_id="cb_123", text="Done!")
    
    assert success is True
    args, kwargs = mock_post.call_args
    assert kwargs["data"]["callback_query_id"] == "cb_123"
    assert kwargs["data"]["text"] == "Done!"


@pytest.mark.asyncio
async def test_async_set_commands() -> None:
    client = AsyncClient("123456:ABC-DEF")
    client.request = AsyncMock(return_value=True)

    commands = [
        BotCommand(command="start", description="Start"),
        BotCommand(command="help", description="Help")
    ]
    
    success = await client.set_my_commands(commands=commands)
    assert success is True
    
    args, kwargs = client.request.call_args
    assert args[0] == "setMyCommands"
    # Ensure commands list was serialized to JSON
    assert '[{"command": "start", "description": "Start"}' in kwargs["data"]["commands"]
