"""Comprehensive tests for the Account API."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from pysoroush.account import AsyncClient, Client


@pytest.fixture(autouse=True)
def mock_engine():
    with patch('pysoroush.account.async_client.StringSession'), \
         patch('pysoroush.account.async_client.SoroushClient'):
        yield


def _mock_client():
    """Create an AsyncClient with a fully-mocked underlying SPlusthon client."""
    client = AsyncClient(session_string="x")
    m = AsyncMock()
    # is_connected is a synchronous method
    m.is_connected = MagicMock(return_value=True)
    client._client = m
    return client, m


# ============ Basic ============
@pytest.mark.asyncio
async def test_init():
    c = AsyncClient(session_string="x")
    assert c.session_string == "x"


@pytest.mark.asyncio
async def test_send_message():
    c, m = _mock_client()
    m.send_message = AsyncMock(return_value="ok")
    assert await c.send_message(1, "hi") == "ok"


# ============ Media ============
@pytest.mark.asyncio
async def test_send_file():
    c, m = _mock_client()
    m.send_file = AsyncMock(return_value="ok")
    assert await c.send_file("me", "f.jpg") == "ok"


@pytest.mark.asyncio
async def test_send_photo():
    c, m = _mock_client()
    m.send_file = AsyncMock(return_value="ok")
    await c.send_photo("me", "p.jpg")
    assert m.send_file.call_args.kwargs["force_document"] is False


@pytest.mark.asyncio
async def test_send_document():
    c, m = _mock_client()
    m.send_file = AsyncMock(return_value="ok")
    await c.send_document("me", "d.pdf")
    assert m.send_file.call_args.kwargs["force_document"] is True


@pytest.mark.asyncio
async def test_forward_messages():
    c, m = _mock_client()
    m.forward_messages = AsyncMock(return_value="fwd")
    assert await c.forward_messages("me", [1], 2) == "fwd"


@pytest.mark.asyncio
async def test_send_reaction():
    c, m = _mock_client()
    m.get_input_entity = AsyncMock(return_value="peer")
    m.return_value = "reacted"
    result = await c.send_reaction("me", 1, "👍")
    assert result == "reacted"


# ============ Reading ============
@pytest.mark.asyncio
async def test_get_messages():
    c, m = _mock_client()
    m.get_messages = AsyncMock(return_value=[{"id": 1}])
    assert len(await c.get_messages("me")) == 1


@pytest.mark.asyncio
async def test_iter_messages():
    c, m = _mock_client()

    async def fi(e, limit=None, **kw):
        for i in range(3):
            yield i

    m.iter_messages = fi
    result = [i async for i in c.iter_messages("me")]
    assert result == [0, 1, 2]


@pytest.mark.asyncio
async def test_search_messages():
    c, m = _mock_client()
    m.get_messages = AsyncMock(return_value=[{"id": 1}])
    await c.search_messages("me", "hello")
    assert m.get_messages.call_args.kwargs["search"] == "hello"


# ============ Managing messages ============
@pytest.mark.asyncio
async def test_edit_message():
    c, m = _mock_client()
    m.edit_message = AsyncMock(return_value="ok")
    assert await c.edit_message("me", 1, "new") == "ok"


@pytest.mark.asyncio
async def test_delete_messages():
    c, m = _mock_client()
    m.delete_messages = AsyncMock(return_value=[1])
    assert await c.delete_messages("me", [1]) == [1]


@pytest.mark.asyncio
async def test_pin_message():
    c, m = _mock_client()
    m.pin_message = AsyncMock(return_value=True)
    assert await c.pin_message("me", 1) is True


@pytest.mark.asyncio
async def test_unpin_message():
    c, m = _mock_client()
    m.unpin_message = AsyncMock(return_value=True)
    assert await c.unpin_message("me", 1) is True


@pytest.mark.asyncio
async def test_mark_as_read():
    c, m = _mock_client()
    m.send_read_acknowledge = AsyncMock(return_value=True)
    assert await c.mark_as_read("me") is True


@pytest.mark.asyncio
async def test_send_chat_action():
    c, m = _mock_client()
    m.get_input_entity = AsyncMock(return_value="peer")
    m.return_value = True  # the raw SetTypingRequest call
    assert await c.send_chat_action("me", "typing") is True


# ============ Chat management ============
@pytest.mark.asyncio
async def test_create_group():
    c, m = _mock_client()
    mock_res = MagicMock()
    mock_res.chats = ["mock_group"]
    m.return_value = mock_res
    assert await c.create_group("T", [1, 2]) == "mock_group"


@pytest.mark.asyncio
async def test_create_channel():
    c, m = _mock_client()
    mock_res = MagicMock()
    mock_res.chats = ["mock_ch"]
    m.return_value = mock_res
    assert await c.create_channel("T", about="desc") == "mock_ch"


@pytest.mark.asyncio
async def test_join_chat():
    c, m = _mock_client()
    m.return_value = "joined"
    assert await c.join_chat("ch") == "joined"


@pytest.mark.asyncio
async def test_leave_chat():
    c, m = _mock_client()
    m.return_value = "left"
    assert await c.leave_chat("ch") == "left"


@pytest.mark.asyncio
async def test_export_invite_link():
    c, m = _mock_client()
    mock_res = MagicMock()
    mock_res.link = "https://x"
    m.return_value = mock_res
    assert await c.export_chat_invite_link("ch") == "https://x"


# ============ Admin ============
@pytest.mark.asyncio
async def test_kick_participant():
    c, m = _mock_client()
    m.kick_participant = AsyncMock(return_value=True)
    assert await c.kick_participant("ch", 123) is True


@pytest.mark.asyncio
async def test_edit_admin():
    c, m = _mock_client()
    m.get_input_entity = AsyncMock(return_value="peer")
    m.return_value = "promoted"
    result = await c.edit_admin("ch", 123, post_messages=True)
    assert result == "promoted"


# ============ Profile ============
@pytest.mark.asyncio
async def test_update_profile():
    c, m = _mock_client()
    m.return_value = True
    assert await c.update_profile(first_name="Ali") is True


@pytest.mark.asyncio
async def test_update_username():
    c, m = _mock_client()
    m.return_value = True
    assert await c.update_username("ali") is True


@pytest.mark.asyncio
async def test_set_profile_photo():
    c, m = _mock_client()
    m.upload_file = AsyncMock(return_value="uploaded")
    m.return_value = "photo_set"
    assert await c.set_profile_photo("/path/p.jpg") == "photo_set"


@pytest.mark.asyncio
async def test_delete_profile_photos():
    c, m = _mock_client()
    m.return_value = "deleted"
    assert await c.delete_profile_photos(["p1"]) == "deleted"


# ============ Media download ============
@pytest.mark.asyncio
async def test_download_media():
    c, m = _mock_client()
    m.download_media = AsyncMock(return_value="/path/x.jpg")
    assert await c.download_media("media") == "/path/x.jpg"


@pytest.mark.asyncio
async def test_download_profile_photo():
    c, m = _mock_client()
    m.download_profile_photo = AsyncMock(return_value="/path/p.jpg")
    assert await c.download_profile_photo("u") == "/path/p.jpg"


# ============ Event handlers ============
@pytest.mark.asyncio
async def test_on_message_registers():
    c, m = _mock_client()
    m.add_event_handler = MagicMock()

    @c.on_message(pattern="hi")
    def handler(msg):
        pass

    assert m.add_event_handler.called


@pytest.mark.asyncio
async def test_on_edited_message_registers():
    c, m = _mock_client()
    m.add_event_handler = MagicMock()

    @c.on_edited_message()
    def handler(msg):
        pass

    assert m.add_event_handler.called


@pytest.mark.asyncio
async def test_on_deleted_message_registers():
    c, m = _mock_client()
    m.add_event_handler = MagicMock()

    @c.on_deleted_message()
    def handler(event):
        pass

    assert m.add_event_handler.called


@pytest.mark.asyncio
async def test_on_user_update_registers():
    c, m = _mock_client()
    m.add_event_handler = MagicMock()

    @c.on_user_update()
    def handler(event):
        pass

    assert m.add_event_handler.called


@pytest.mark.asyncio
async def test_on_chat_action_registers():
    c, m = _mock_client()
    m.add_event_handler = MagicMock()

    @c.on_chat_action()
    def handler(event):
        pass

    assert m.add_event_handler.called


# ============ Sync wrappers ============
def test_sync_send_message():
    c = Client(session_string="x")
    mock = MagicMock()
    mock.is_connected = MagicMock(return_value=True)
    mock.send_message = AsyncMock(return_value="sync-ok")
    c._async._client = mock
    try:
        assert c.send_message("me", "hi") == "sync-ok"
    finally:
        if c._loop and not c._loop.is_closed():
            c._loop.close()


def test_sync_send_photo():
    c = Client(session_string="x")
    mock = MagicMock()
    mock.is_connected = MagicMock(return_value=True)
    mock.send_file = AsyncMock(return_value="sync-photo")
    c._async._client = mock
    try:
        assert c.send_photo("me", "p.jpg") == "sync-photo"
    finally:
        if c._loop and not c._loop.is_closed():
            c._loop.close()


def test_sync_create_channel():
    c = Client(session_string="x")
    # Use AsyncMock for the client so it can be awaited, and override sync methods
    mock = AsyncMock()
    mock.is_connected = MagicMock(return_value=True)
    mock_res = MagicMock()
    mock_res.chats = ["sync-ch"]
    mock.return_value = mock_res
    c._async._client = mock
    try:
        assert c.create_channel("T") == "sync-ch"
    finally:
        if c._loop and not c._loop.is_closed():
            c._loop.close()
