"""
Constants used throughout the PySoroush Bot package.

All values in this module are read-only and should not be modified
by the user. They reflect the official Soroush Plus Bot API behavior.
"""

from __future__ import annotations

from typing import Final, Tuple

# Base URL of the Soroush Plus Bot API.
# The final request URL is: {BASE_URL}/bot{TOKEN}/{METHOD_NAME}
BASE_URL: Final[str] = "https://api.splus.ir"

# URL used to download files uploaded to Soroush Plus.
# The final download URL is: {FILE_URL}/bot{TOKEN}/{file_path}
FILE_URL: Final[str] = "https://api.splus.ir/file"

# API version of the Bot API this library targets.
API_VERSION: Final[str] = "1.0"

# File size limits (in bytes) enforced by the Bot API.
MAX_PHOTO_SIZE: Final[int] = 10 * 1024 * 1024         # 10 MB for photos
MAX_FILE_SIZE: Final[int] = 50 * 1024 * 1024          # 50 MB for other uploads
MAX_DOWNLOAD_SIZE: Final[int] = 20 * 1024 * 1024      # 20 MB for downloads

# Default long-polling settings for getUpdates.
DEFAULT_POLLING_TIMEOUT: Final[int] = 30
DEFAULT_POLLING_LIMIT: Final[int] = 100

# Default webhook settings.
DEFAULT_WEBHOOK_MAX_CONNECTIONS: Final[int] = 40
DEFAULT_WEBHOOK_PORT: Final[int] = 8443
WEBHOOK_ALLOWED_PORTS: Final[Tuple[int, ...]] = (443, 80, 88, 8443)

# Server-side retention periods.
UPDATE_RETENTION_HOURS: Final[int] = 24
FILE_URL_VALIDITY_HOURS: Final[int] = 1

# Default network timeout (in seconds) used when the user does not set one.
DEFAULT_REQUEST_TIMEOUT: Final[int] = 30

# Supported parse modes for message text.
PARSE_MODE_MARKDOWN: Final[str] = "Markdown"
PARSE_MODE_MARKDOWN_V2: Final[str] = "MarkdownV2"
PARSE_MODE_HTML: Final[str] = "HTML"

SUPPORTED_PARSE_MODES: Final[Tuple[str, ...]] = (
    PARSE_MODE_MARKDOWN,
    PARSE_MODE_MARKDOWN_V2,
    PARSE_MODE_HTML,
)

# Auto-retry defaults (feature #2: auto-retry with backoff).
DEFAULT_RETRY_ATTEMPTS: Final[int] = 3
DEFAULT_RETRY_BACKOFF: Final[float] = 1.5
DEFAULT_RETRY_INITIAL_DELAY: Final[float] = 1.0
