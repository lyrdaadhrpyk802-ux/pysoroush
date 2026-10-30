"""Tests for the new sending methods (photo, document, etc)."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import aiohttp

from pysoroush.bot.client import Client
from pysoroush.bot.async_client import AsyncClient
from pysoroush.bot.types import Message, InputFile


@patch("requests.Session.post")
def test_send_photo_with_file(mock_post: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ok": True,
        "result": {
            "message_id": 1,
            "date": 123,
            "chat": {"id": 1, "type": "private"},
            "photo": [{"file_id": "123", "file_unique_id": "abc", "width": 100, "height": 100}]
        }
    }
    mock_post.return_value = mock_response

    client = Client("123456:ABC-DEF")
    
    with patch("pysoroush.bot.types.input_file.InputFile._open") as mock_open:
        mock_file_obj = MagicMock()
        mock_file_obj.closed = False
        mock_open.return_value = mock_file_obj

        photo_input = InputFile("fake_path.jpg", filename="fake_path.jpg")
        msg = client.send_photo(chat_id=1, photo=photo_input, caption="Test")
        
        assert isinstance(msg, Message)
        assert msg.message_id == 1
        assert msg.photo[0].file_id == "123"

        args, kwargs = mock_post.call_args
        assert kwargs["files"]["photo"][0] == "fake_path.jpg"
        assert kwargs["data"]["caption"] == "Test"


@patch("requests.Session.post")
def test_send_location(mock_post: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ok": True,
        "result": {
            "message_id": 2,
            "date": 123,
            "chat": {"id": 1, "type": "private"},
            "location": {"latitude": 35.0, "longitude": 51.0}
        }
    }
    mock_post.return_value = mock_response

    client = Client("123456:ABC-DEF")
    msg = client.send_location(chat_id=1, latitude=35.0, longitude=51.0)

    assert msg.message_id == 2
    args, kwargs = mock_post.call_args
    assert kwargs["data"]["latitude"] == 35.0
    assert kwargs["data"]["longitude"] == 51.0


@pytest.mark.asyncio
async def test_async_send_document_with_file() -> None:
    client = AsyncClient("123456:ABC-DEF")
    
    mock_post = MagicMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {
        "ok": True,
        "result": {
            "message_id": 3,
            "date": 123,
            "chat": {"id": 1, "type": "private"},
            "document": {"file_id": "doc1", "file_unique_id": "doc1"}
        }
    }
    
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_response)
    mock_cm.__aexit__ = AsyncMock()
    mock_post.return_value = mock_cm
    
    mock_session = MagicMock()
    mock_session.closed = False
    mock_session.post = mock_post
    mock_session.close = AsyncMock()
    client.session = mock_session

    with patch("pysoroush.bot.types.input_file.InputFile._open") as mock_open:
        mock_file_obj = MagicMock()
        mock_file_obj.closed = False
        mock_open.return_value = mock_file_obj

        doc_input = InputFile("fake_doc.pdf", filename="fake_doc.pdf")
        msg = await client.send_document(
            chat_id=1, document=doc_input, caption="File"
        )

        assert msg.message_id == 3
        assert msg.document.file_id == "doc1"
        
        args, kwargs = mock_post.call_args
        # Fixed assertion to check for the correct aiohttp FormData object
        assert isinstance(kwargs["data"], aiohttp.FormData)

    await client.close()
