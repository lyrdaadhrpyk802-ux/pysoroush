"""Tests for the newly added advanced features in the Account API."""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch

from pysoroush.account import AsyncClient


@pytest.fixture(autouse=True)
def mock_engine():
    with patch('pysoroush.account.async_client.StringSession'), \
         patch('pysoroush.account.async_client.SoroushClient'):
        yield


def _mock_client():
    client = AsyncClient(session_string="x")
    m = AsyncMock()
    m.is_connected = MagicMock(return_value=True)
    client._client = m
    return client, m


# === Special Messages ===
@pytest.mark.asyncio
async def test_send_scheduled_message():
    c, m = _mock_client()
    m.send_message = AsyncMock(return_value="scheduled")
    dt = datetime(2024, 12, 31, 12, 0)
    assert await c.send_scheduled_message(1, "hi", dt) == "scheduled"
    assert m.send_message.call_args.kwargs["schedule"] == dt


@pytest.mark.asyncio
async def test_send_sticker():
    c, m = _mock_client()
    m.send_file = AsyncMock(return_value="sticker")
    assert await c.send_sticker(1, "s.webp") == "sticker"
    assert m.send_file.call_args.kwargs["force_document"] is False


@pytest.mark.asyncio
async def test_send_location():
    c, m = _mock_client()
    m.send_file = AsyncMock(return_value="loc")
    assert await c.send_location(1, 35.0, 51.0) == "loc"
    assert m.send_file.called


@pytest.mark.asyncio
async def test_send_contact():
    c, m = _mock_client()
    m.send_file = AsyncMock(return_value="contact")
    assert await c.send_contact(1, "+98912", "Ali") == "contact"
    assert m.send_file.called


@pytest.mark.asyncio
async def test_send_poll():
    c, m = _mock_client()
    m.send_file = AsyncMock(return_value="poll")
    assert await c.send_poll(1, "Question?", ["A", "B"]) == "poll"
    assert m.send_file.called


# === Advanced Management ===
@pytest.mark.asyncio
async def test_block_user():
    c, m = _mock_client()
    m.get_input_entity = AsyncMock(return_value="peer")
    m.return_value = True
    assert await c.block_user(123) is True


@pytest.mark.asyncio
async def test_unblock_user():
    c, m = _mock_client()
    m.get_input_entity = AsyncMock(return_value="peer")
    m.return_value = True
    assert await c.unblock_user(123) is True


@pytest.mark.asyncio
async def test_clear_history():
    c, m = _mock_client()
    m.get_input_entity = AsyncMock(return_value="peer")
    m.return_value = True
    assert await c.clear_history("chat") is True


@pytest.mark.asyncio
async def test_save_draft():
    c, m = _mock_client()
    m.get_input_entity = AsyncMock(return_value="peer")
    m.return_value = True
    assert await c.save_draft("chat", "hello") is True


@pytest.mark.asyncio
async def test_get_full_user():
    c, m = _mock_client()
    m.get_input_entity = AsyncMock(return_value="peer")
    m.return_value = {"id": 1, "bio": "Hello"}
    result = await c.get_full_user(123)
    assert result["bio"] == "Hello"


# === Advanced Capabilities ===
@pytest.mark.asyncio
async def test_get_stats():
    c, m = _mock_client()
    m.get_input_entity = AsyncMock(return_value="channel")
    m.return_value = {"views": 1000}
    result = await c.get_stats("channel")
    assert result["views"] == 1000


@pytest.mark.asyncio
async def test_get_folders():
    c, m = _mock_client()
    m.return_value = ["folder1", "folder2"]
    result = await c.get_folders()
    assert len(result) == 2


@pytest.mark.asyncio
async def test_edit_folder():
    c, m = _mock_client()
    m.return_value = True
    assert await c.edit_folder(1, "Friends") is True
