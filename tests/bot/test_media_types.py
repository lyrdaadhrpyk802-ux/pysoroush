"""Tests for InputFile, InputMedia, File, and BotCommand types."""

import os
import pytest
from pysoroush.bot.types import (
    InputFile, InputMediaPhoto, File, BotCommand
)


def test_input_file_from_bytes() -> None:
    data = b"fake_image_data"
    f = InputFile(data, filename="test.jpg")
    obj = f._open()
    assert obj.read() == data
    assert f.filename == "test.jpg"
    f.close()


def test_input_file_from_path() -> None:
    # Create a dummy file
    temp_path = "/storage/emulated/0/pysoroush/test_temp.txt"
    with open(temp_path, "w") as file:
        file.write("hello")

    try:
        f = InputFile(temp_path)
        obj = f._open()
        assert obj.read() == b"hello"
        assert f.filename == "test_temp.txt"
        f.close()
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_input_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        f = InputFile("/storage/emulated/0/pysoroush/does_not_exist_12345.jpg")
        f._open()


def test_input_media_photo_to_dict() -> None:
    media = InputMediaPhoto(media="file_id_123", caption="Nice photo")
    d = media.to_dict()
    assert d["type"] == "photo"
    assert d["media"] == "file_id_123"
    assert d["caption"] == "Nice photo"


def test_file_type() -> None:
    f = File(file_id="123", file_unique_id="abc", file_path="photos/file_1.jpg")
    assert f.file_id == "123"
    assert f.file_path == "photos/file_1.jpg"


def test_bot_command() -> None:
    cmd = BotCommand(command="start", description="Start the bot")
    d = cmd.to_dict()
    assert d == {"command": "start", "description": "Start the bot"}
