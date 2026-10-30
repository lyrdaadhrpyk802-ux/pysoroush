"""
Custom exceptions for the Soroush Plus Account API.
"""

class SoroushAccountError(Exception):
    """Base exception for all Account API errors."""
    pass

class AuthError(SoroushAccountError):
    """Raised when authentication fails (e.g., wrong code)."""
    pass

class PasswordRequiredError(AuthError):
    """Raised when a two-step verification password is required."""
    pass
