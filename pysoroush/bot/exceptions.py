"""
Exception hierarchy for PySoroush.

Every library-specific exception inherits from :class:`SoroushError`, so
users can catch any library error with a single ``except SoroushError``.
The function :func:`raise_for_error` inspects a raw Bot API response and
raises the most specific exception available.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class SoroushError(Exception):
    """Base class for all PySoroush exceptions."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return self.message


# ---------------------------------------------------------------------------
# API-level errors (returned by the server as {"ok": false, ...})
# ---------------------------------------------------------------------------

class SoroushAPIError(SoroushError):
    """
    Raised when the Bot API returns an unsuccessful response.

    The server replies with a JSON object containing ``ok``,
    ``error_code``, ``description`` and (optionally) ``parameters``.
    """

    def __init__(
        self,
        description: str,
        error_code: Optional[int] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.error_code = error_code
        self.description = description
        self.parameters = parameters or {}

        if error_code is not None:
            message = f"[{error_code}] {description}"
        else:
            message = description

        super().__init__(message)


class RateLimitError(SoroushAPIError):
    """
    Raised when the bot hits the API rate limit (HTTP 429).

    The ``retry_after`` attribute tells the caller how many seconds to
    wait before retrying the request.
    """

    def __init__(self, description: str, retry_after: int) -> None:
        self.retry_after = retry_after
        super().__init__(
            description=description,
            error_code=429,
            parameters={"retry_after": retry_after},
        )


class UnauthorizedError(SoroushAPIError):
    """Raised when the bot token is invalid or revoked (HTTP 401)."""

    def __init__(self, description: str = "Unauthorized") -> None:
        super().__init__(description=description, error_code=401)


class ForbiddenError(SoroushAPIError):
    """Raised when the bot lacks permission for the requested action (HTTP 403)."""

    def __init__(self, description: str = "Forbidden") -> None:
        super().__init__(description=description, error_code=403)


class BadRequestError(SoroushAPIError):
    """Raised when the API rejects a request due to invalid parameters (HTTP 400)."""

    def __init__(self, description: str = "Bad request") -> None:
        super().__init__(description=description, error_code=400)


class NotFoundError(SoroushAPIError):
    """Raised when the requested resource does not exist (HTTP 404)."""

    def __init__(self, description: str = "Not found") -> None:
        super().__init__(description=description, error_code=404)


class ChatNotFoundError(NotFoundError):
    """Raised when the requested chat cannot be found."""

    def __init__(self, description: str = "Chat not found") -> None:
        super().__init__(description=description)


class MessageNotFoundError(NotFoundError):
    """Raised when the requested message cannot be found."""

    def __init__(self, description: str = "Message not found") -> None:
        super().__init__(description=description)


class FileTooLargeError(BadRequestError):
    """Raised when a file exceeds the limits accepted by the Bot API."""

    def __init__(self, description: str = "File is too large") -> None:
        super().__init__(description=description)


# ---------------------------------------------------------------------------
# Network-level errors (thrown by the transport layer)
# ---------------------------------------------------------------------------

class SoroushNetworkError(SoroushError):
    """Base class for network-level failures."""


class SoroushTimeoutError(SoroushNetworkError):
    """Raised when a request to the Bot API times out."""


class SoroushConnectionError(SoroushNetworkError):
    """Raised when a connection to the Bot API cannot be established."""


class SoroushServerError(SoroushNetworkError):
    """Raised when the Bot API server responds with a 5xx status code."""

    def __init__(self, status_code: int, description: str = "Server error") -> None:
        self.status_code = status_code
        super().__init__(f"[{status_code}] {description}")


# ---------------------------------------------------------------------------
# Client-side errors
# ---------------------------------------------------------------------------

class SoroushValidationError(SoroushError):
    """Raised when client-side validation of a parameter fails."""


class WebhookError(SoroushError):
    """Raised when a webhook operation fails."""


class PollingError(SoroushError):
    """Raised when a long-polling operation fails."""


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def raise_for_error(data: Dict[str, Any]) -> None:
    """
    Inspect a Bot API response and raise the appropriate exception if the
    ``ok`` field is ``False``.

    Parameters
    ----------
    data : dict
        The decoded JSON response from the Bot API.

    Raises
    ------
    SoroushAPIError
        A subclass matching the returned ``error_code``.
    """
    if data.get("ok", False):
        return

    description: str = data.get("description", "Unknown error")
    error_code: Optional[int] = data.get("error_code")
    parameters: Dict[str, Any] = data.get("parameters") or {}

    if error_code == 429:
        retry_after = int(parameters.get("retry_after", 0))
        raise RateLimitError(description=description, retry_after=retry_after)

    if error_code == 401:
        raise UnauthorizedError(description=description)

    if error_code == 403:
        raise ForbiddenError(description=description)

    if error_code == 400:
        lowered = description.lower()
        if "too large" in lowered or "too big" in lowered:
            raise FileTooLargeError(description=description)
        raise BadRequestError(description=description)

    if error_code == 404:
        lowered = description.lower()
        if "chat" in lowered:
            raise ChatNotFoundError(description=description)
        if "message" in lowered:
            raise MessageNotFoundError(description=description)
        raise NotFoundError(description=description)

    raise SoroushAPIError(
        description=description,
        error_code=error_code,
        parameters=parameters,
    )
