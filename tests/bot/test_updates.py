"""Tests for getUpdates and Webhook methods."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from pysoroush.bot.client import Client
from pysoroush.bot.async_client import AsyncClient
from pysoroush.bot.types import Update, WebhookInfo


@patch("requests.Session.post")
def test_sync_get_updates(mock_post: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ok": True,
        "result": [
            {
                "update_id": 1234,
                "message": {
                    "message_id": 1,
                    "date": 123456789,
                    "chat": {"id": 1, "type": "private"},
                    "text": "hello"
                }
            }
        ]
    }
    mock_post.return_value = mock_response

    client = Client("123456:ABC-DEF")
    updates = client.get_updates(offset=0, limit=10, timeout=5)

    assert len(updates) == 1
    assert isinstance(updates[0], Update)
    assert updates[0].update_id == 1234
    assert updates[0].message.text == "hello"


@patch("requests.Session.post")
def test_sync_webhook_info(mock_post: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ok": True,
        "result": {
            "url": "https://example.com/webhook",
            "has_custom_certificate": False,
            "pending_update_count": 5
        }
    }
    mock_post.return_value = mock_response

    client = Client("123456:ABC-DEF")
    info = client.get_webhook_info()

    assert isinstance(info, WebhookInfo)
    assert info.url == "https://example.com/webhook"
    assert info.pending_update_count == 5


@pytest.mark.asyncio
async def test_async_get_updates() -> None:
    client = AsyncClient("123456:ABC-DEF")
    client.request = AsyncMock(return_value=[
        {
            "update_id": 999,
            "callback_query": {
                "id": "cb1",
                "from": {"id": 1, "is_bot": False, "first_name": "Ali"},
                "data": "btn_click"
            }
        }
    ])

    updates = await client.get_updates()
    assert len(updates) == 1
    assert isinstance(updates[0], Update)
    assert updates[0].update_id == 999
    assert updates[0].callback_query.id == "cb1"
    assert updates[0].callback_query.from_user.first_name == "Ali"
