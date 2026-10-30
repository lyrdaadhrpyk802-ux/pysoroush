"""Tests for the synchronous Client."""

from unittest.mock import patch, MagicMock
import pytest
import requests

from pysoroush.bot.client import Client
from pysoroush.bot.exceptions import (
    RateLimitError,
    SoroushNetworkError,
    SoroushValidationError,
)


def test_invalid_token_raises_error() -> None:
    with pytest.raises(SoroushValidationError):
        Client("invalid_token_without_colon")


@patch("requests.Session.post")
def test_successful_request(mock_post: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ok": True, "result": {"id": 123}}
    mock_post.return_value = mock_response

    client = Client("123456:ABC-DEF")
    result = client.request("getMe")

    assert result == {"id": 123}
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert "123456:ABC-DEF/getMe" in args[0]


@patch("time.sleep")
@patch("requests.Session.post")
def test_rate_limit_retries(mock_post: MagicMock, mock_sleep: MagicMock) -> None:
    # First response: 429 Rate Limit
    mock_res_429 = MagicMock()
    mock_res_429.status_code = 429
    mock_res_429.json.return_value = {
        "ok": False,
        "error_code": 429,
        "description": "Too Many Requests",
        "parameters": {"retry_after": 5},
    }

    # Second response: 200 OK
    mock_res_200 = MagicMock()
    mock_res_200.status_code = 200
    mock_res_200.json.return_value = {"ok": True, "result": "success"}

    mock_post.side_effect = [mock_res_429, mock_res_200]

    client = Client("123456:ABC-DEF")
    result = client.request("sendMessage", data={"chat_id": 1})

    assert result == "success"
    assert mock_post.call_count == 2
    mock_sleep.assert_called_once_with(5)


@patch("time.sleep")
@patch("requests.Session.post")
def test_network_error_retries(mock_post: MagicMock, mock_sleep: MagicMock) -> None:
    # First attempt: ConnectionError
    mock_post.side_effect = [
        requests.exceptions.ConnectionError("Connection aborted"),
        MagicMock(status_code=200, json=lambda: {"ok": True, "result": "ok"}),
    ]

    client = Client("123456:ABC-DEF", retries=1)
    result = client.request("getMe")

    assert result == "ok"
    assert mock_post.call_count == 2
    mock_sleep.assert_called_once()


@patch("time.sleep")
@patch("requests.Session.post")
def test_max_retries_exceeded(mock_post: MagicMock, mock_sleep: MagicMock) -> None:
    # Always ConnectionError
    mock_post.side_effect = requests.exceptions.ConnectionError("Connection aborted")

    client = Client("123456:ABC-DEF", retries=2)
    
    with pytest.raises(SoroushNetworkError):
        client.request("getMe")

    # 1 initial + 2 retries = 3 attempts
    assert mock_post.call_count == 3
    assert mock_sleep.call_count == 2
