"""Tests for WebApp data validation."""

import pytest
from pysoroush.bot.webapp import validate_webapp_data


def test_validate_webapp_data_success() -> None:
    # Test data constructed according to the Soroush Plus docs
    bot_token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    
    # data-check-string: auth_date=1600000000\nquery_id=AAH12345
    # We need to pre-calculate the hash for this specific test
    import hmac, hashlib
    
    data_check_string = "auth_date=1600000000\nquery_id=AAH12345"
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    valid_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    init_data = f"query_id=AAH12345&auth_date=1600000000&hash={valid_hash}"
    
    assert validate_webapp_data(init_data, bot_token) is True


def test_validate_webapp_data_invalid_hash() -> None:
    bot_token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    init_data = "query_id=AAH12345&auth_date=1600000000&hash=invalidhash123"
    
    assert validate_webapp_data(init_data, bot_token) is False


def test_validate_webapp_data_missing_hash() -> None:
    bot_token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    init_data = "query_id=AAH12345&auth_date=1600000000"
    
    assert validate_webapp_data(init_data, bot_token) is False
