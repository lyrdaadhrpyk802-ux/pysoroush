"""Tests for the final batch of features (100% coverage)."""

import pytest
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


# === Raw API access ===
@pytest.mark.asyncio
async def test_raw_call():
    c, m = _mock_client()
    m.return_value = "raw_result"
    assert await c("some_request") == "raw_result"


@pytest.mark.asyncio
async def test_raw_alias():
    c, m = _mock_client()
    m.return_value = "raw_alias"
    assert await c.raw("req") == "raw_alias"


# === Advanced invite / members ===
@pytest.mark.asyncio
async def test_join_chat_invite():
    c, m = _mock_client()
    m.return_value = "joined"
    assert await c.join_chat_invite("hash123") == "joined"


@pytest.mark.asyncio
async def test_add_chat_user():
    c, m = _mock_client()
    m.get_input_entity = AsyncMock(side_effect=lambda x: f"peer_{x}")
    m.return_value = "added"
    assert await c.add_chat_user("chat", "user") == "added"


@pytest.mark.asyncio
async def test_invite_to_channel():
    c, m = _mock_client()
    m.get_input_entity = AsyncMock(side_effect=lambda x: f"peer_{x}")
    m.return_value = "invited"
    assert await c.invite_to_channel("ch", ["u1", "u2"]) == "invited"


# === Advanced info ===
@pytest.mark.asyncio
async def test_get_full_channel():
    c, m = _mock_client()
    m.get_input_entity = AsyncMock(return_value="peer")
    m.return_value = {"about": "channel"}
    assert (await c.get_full_channel("ch"))["about"] == "channel"


@pytest.mark.asyncio
async def test_get_profile_photos():
    c, m = _mock_client()
    m.get_profile_photos = AsyncMock(return_value={"count": 5})
    assert (await c.get_profile_photos("user"))["count"] == 5


@pytest.mark.asyncio
async def test_get_messages_views():
    c, m = _mock_client()
    m.get_input_entity = AsyncMock(return_value="peer")
    m.return_value = {"views": 100}
    assert (await c.get_messages_views("ch", [1, 2]))["views"] == 100


@pytest.mark.asyncio
async def test_get_input_entity():
    c, m = _mock_client()
    m.get_input_entity = AsyncMock(return_value="peer")
    assert await c.get_input_entity("x") == "peer"


@pytest.mark.asyncio
async def test_get_peer_id():
    c, m = _mock_client()
    m.get_peer_id = AsyncMock(return_value=12345)
    assert await c.get_peer_id("x") == 12345


# === Folder / dialog management ===
@pytest.mark.asyncio
async def test_pin_dialog():
    c, m = _mock_client()
    m.get_input_entity = AsyncMock(return_value="peer")
    m.return_value = True
    assert await c.pin_dialog("ch") is True


@pytest.mark.asyncio
async def test_unpin_dialog():
    c, m = _mock_client()
    m.get_input_entity = AsyncMock(return_value="peer")
    m.return_value = True
    assert await c.unpin_dialog("ch") is True


@pytest.mark.asyncio
async def test_mute_chat():
    c, m = _mock_client()
    m.get_input_entity = AsyncMock(return_value="peer")
    m.return_value = True
    assert await c.mute_chat("ch") is True


@pytest.mark.asyncio
async def test_unmute_chat():
    c, m = _mock_client()
    m.get_input_entity = AsyncMock(return_value="peer")
    m.return_value = True
    assert await c.unmute_chat("ch") is True


@pytest.mark.asyncio
async def test_archive_chat():
    c, m = _mock_client()
    m.get_input_entity = AsyncMock(return_value="peer")
    m.return_value = True
    assert await c.archive_chat("ch") is True


@pytest.mark.asyncio
async def test_unarchive_chat():
    c, m = _mock_client()
    m.get_input_entity = AsyncMock(return_value="peer")
    m.return_value = True
    assert await c.unarchive_chat("ch") is True


# === Catch up ===
@pytest.mark.asyncio
async def test_catch_up():
    c, m = _mock_client()
    m.catch_up = AsyncMock(return_value=None)
    await c.catch_up()
    assert m.catch_up.called


# === Async iterators ===
@pytest.mark.asyncio
async def test_iter_dialogs():
    c, m = _mock_client()

    async def gen(limit=None):
        for i in range(3):
            yield {"id": i}

    m.iter_dialogs = gen
    results = [d async for d in c.iter_dialogs()]
    assert len(results) == 3


@pytest.mark.asyncio
async def test_iter_participants():
    c, m = _mock_client()

    async def gen(entity, limit=None, **kw):
        for i in range(2):
            yield {"id": i}

    m.iter_participants = gen
    results = [p async for p in c.iter_participants("ch")]
    assert len(results) == 2


# === New event handlers ===
@pytest.mark.asyncio
async def test_on_message_read_registers():
    c, m = _mock_client()
    m.add_event_handler = MagicMock()

    @c.on_message_read()
    def h(evt):
        pass

    assert m.add_event_handler.called


@pytest.mark.asyncio
async def test_on_album_registers():
    c, m = _mock_client()
    m.add_event_handler = MagicMock()

    @c.on_album()
    def h(evt):
        pass

    assert m.add_event_handler.called


@pytest.mark.asyncio
async def test_on_raw_registers():
    c, m = _mock_client()
    m.add_event_handler = MagicMock()

    @c.on_raw()
    def h(evt):
        pass

    assert m.add_event_handler.called
