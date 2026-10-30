"""Tests for the exception hierarchy in pysoroush.bot.exceptions."""

import pytest

from pysoroush.bot.exceptions import (
    BadRequestError,
    ChatNotFoundError,
    FileTooLargeError,
    ForbiddenError,
    MessageNotFoundError,
    NotFoundError,
    RateLimitError,
    SoroushAPIError,
    SoroushConnectionError,
    SoroushError,
    SoroushNetworkError,
    SoroushServerError,
    SoroushTimeoutError,
    SoroushValidationError,
    UnauthorizedError,
    raise_for_error,
)


def test_base_error_inherits_from_exception() -> None:
    assert issubclass(SoroushError, Exception)


def test_all_errors_inherit_from_soroush_error() -> None:
    classes = (
        SoroushAPIError,
        SoroushNetworkError,
        SoroushServerError,
        SoroushTimeoutError,
        SoroushConnectionError,
        SoroushValidationError,
        RateLimitError,
        UnauthorizedError,
        ForbiddenError,
        BadRequestError,
        NotFoundError,
        ChatNotFoundError,
        MessageNotFoundError,
        FileTooLargeError,
    )
    for cls in classes:
        assert issubclass(cls, SoroushError), cls.__name__


def test_api_error_message_contains_code_and_description() -> None:
    err = SoroushAPIError(description="boom", error_code=500)
    assert "500" in str(err)
    assert "boom" in str(err)
    assert err.error_code == 500
    assert err.description == "boom"


def test_api_error_without_code() -> None:
    err = SoroushAPIError(description="plain")
    assert str(err) == "plain"
    assert err.error_code is None


def test_rate_limit_error_exposes_retry_after() -> None:
    err = RateLimitError(description="too many", retry_after=30)
    assert err.retry_after == 30
    assert err.error_code == 429


def test_raise_for_error_returns_on_ok() -> None:
    raise_for_error({"ok": True, "result": []})


def test_raise_for_error_429() -> None:
    with pytest.raises(RateLimitError) as exc_info:
        raise_for_error(
            {
                "ok": False,
                "error_code": 429,
                "description": "Too Many Requests",
                "parameters": {"retry_after": 15},
            }
        )
    assert exc_info.value.retry_after == 15


def test_raise_for_error_401() -> None:
    with pytest.raises(UnauthorizedError):
        raise_for_error(
            {"ok": False, "error_code": 401, "description": "Unauthorized"}
        )


def test_raise_for_error_403() -> None:
    with pytest.raises(ForbiddenError):
        raise_for_error(
            {"ok": False, "error_code": 403, "description": "Forbidden"}
        )


def test_raise_for_error_400_file_too_large() -> None:
    with pytest.raises(FileTooLargeError):
        raise_for_error(
            {"ok": False, "error_code": 400, "description": "File is too large"}
        )


def test_raise_for_error_400_generic() -> None:
    with pytest.raises(BadRequestError):
        raise_for_error(
            {"ok": False, "error_code": 400, "description": "Bad Request"}
        )


def test_raise_for_error_404_chat() -> None:
    with pytest.raises(ChatNotFoundError):
        raise_for_error(
            {"ok": False, "error_code": 404, "description": "Chat not found"}
        )


def test_raise_for_error_404_message() -> None:
    with pytest.raises(MessageNotFoundError):
        raise_for_error(
            {"ok": False, "error_code": 404, "description": "Message not found"}
        )


def test_raise_for_error_404_generic() -> None:
    with pytest.raises(NotFoundError):
        raise_for_error(
            {"ok": False, "error_code": 404, "description": "Not Found"}
        )


def test_raise_for_error_unknown_code() -> None:
    with pytest.raises(SoroushAPIError) as exc_info:
        raise_for_error(
            {"ok": False, "error_code": 999, "description": "Mystery"}
        )
    assert exc_info.value.error_code == 999


def test_chat_not_found_is_not_found() -> None:
    assert issubclass(ChatNotFoundError, NotFoundError)


def test_file_too_large_is_bad_request() -> None:
    assert issubclass(FileTooLargeError, BadRequestError)
