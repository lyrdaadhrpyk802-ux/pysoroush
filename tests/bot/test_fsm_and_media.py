"""Tests for FSM (Context, StateFilter) and MediaGroup."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from pysoroush.bot.bot import Bot
from pysoroush.bot.async_bot import AsyncBot
from pysoroush.bot.types import Message, Chat, Update, InputFile, InputMediaPhoto
from pysoroush.bot.filters import StateFilter


def create_msg(text: str = "hello", chat_id: int = 1) -> Message:
    return Message(message_id=1, date=123, chat=Chat(id=chat_id, type="private"), text=text)


def test_fsm_context() -> None:
    bot = Bot("123456:ABC")
    ctx = bot.get_context(123)
    
    assert ctx.state is None
    ctx.set_state("waiting_for_name")
    assert ctx.state == "waiting_for_name"
    assert bot.get_state(123) == "waiting_for_name"
    
    ctx.set_data("name", "Ali")
    assert ctx.get_data("name") == "Ali"
    
    ctx.clear()
    assert ctx.state is None
    assert ctx.get_data("name") is None


def test_state_filter() -> None:
    bot = Bot("123456:ABC")
    bot.set_state(123, "waiting")
    
    msg = create_msg(chat_id=123)
    msg.state = bot.get_state(123) # simulate injection
    
    f = StateFilter("waiting")
    assert f(msg) is True
    
    f2 = StateFilter("other")
    assert f2(msg) is False


def test_bot_handler_with_state_and_ctx() -> None:
    bot = Bot("123456:ABC")
    bot.set_state(123, "waiting")
    called = False

    @bot.on_message(StateFilter("waiting"))
    def handler(msg: Message, ctx):
        nonlocal called
        called = True
        ctx.set_state("done")
        return True

    update = Update(update_id=1, message=create_msg(chat_id=123))
    bot._process_update(update)
    
    assert called is True
    assert bot.get_state(123) == "done"


def test_handler_stop_propagation() -> None:
    bot = Bot("123456:ABC")
    hit_first = False
    hit_second = False

    @bot.on_message()
    def first_handler(msg: Message):
        nonlocal hit_first
        hit_first = True
        return True # Stop processing here

    @bot.on_message()
    def second_handler(msg: Message):
        nonlocal hit_second
        hit_second = True
        return True

    update = Update(update_id=1, message=create_msg())
    bot._process_update(update)
    
    assert hit_first is True
    assert hit_second is False


@patch("requests.Session.post")
def test_send_media_group_with_attach(mock_post: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ok": True,
        "result": [
            {"message_id": 1, "date": 123, "chat": {"id": 1, "type": "private"}},
            {"message_id": 2, "date": 123, "chat": {"id": 1, "type": "private"}}
        ]
    }
    mock_post.return_value = mock_response

    client = Bot("123456:ABC")
    
    with patch("pysoroush.bot.types.input_file.InputFile._open") as mock_open:
        mock_file_obj = MagicMock()
        mock_file_obj.closed = False
        mock_open.return_value = mock_file_obj

        media = [
            InputMediaPhoto(media="file_id_1"),
            InputMediaPhoto(media=InputFile("path.jpg", filename="img.jpg"), caption="Local file")
        ]
        
        msgs = client.send_media_group(chat_id=1, media=media)
        
        assert len(msgs) == 2
        
        args, kwargs = mock_post.call_args
        assert "attach://file_1" in kwargs["data"]["media"]
        assert kwargs["files"]["file_1"][0] == "img.jpg"
