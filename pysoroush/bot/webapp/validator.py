"""
WebApp data validator for Soroush Plus.
"""

from __future__ import annotations

import hmac
import hashlib
from urllib.parse import parse_qsl
from typing import Dict, Optional


def validate_webapp_data(init_data: str, bot_token: str) -> bool:
    """
    Validates the data received from a Soroush Plus WebApp.
    
    The Soroush Plus documentation specifies that the data check string
    is created by sorting the key-value pairs alphabetically, joined by
    a newline character. The secret key is the HMAC-SHA-256 hash of the
    bot token using the string "WebAppData" as the key.
    
    Args:
        init_data: The raw URL-encoded string from `Soroush.WebApp.initData`.
        bot_token: The bot's authentication token.
        
    Returns:
        True if the data is authentic, False otherwise.
    """
    if not init_data or not bot_token:
        return False

    try:
        # Parse the URL-encoded query string
        parsed_data: Dict[str, str] = dict(parse_qsl(init_data))
    except ValueError:
        return False

    if "hash" not in parsed_data:
        return False

    received_hash = parsed_data.pop("hash")

    # Sort the data alphabetically and join with newlines
    data_check_list = [f"{k}={v}" for k, v in sorted(parsed_data.items())]
    data_check_string = "\n".join(data_check_list)

    # Create the secret key: HMAC-SHA-256(bot_token, "WebAppData")
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()

    # Calculate the HMAC-SHA-256 of the data check string
    calculated_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    # Compare hashes securely
    return hmac.compare_digest(calculated_hash, received_hash)
